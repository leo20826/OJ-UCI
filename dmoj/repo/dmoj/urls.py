import os
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.http import Http404, HttpResponsePermanentRedirect
from django.templatetags.static import static
from django.urls import include, path, re_path, reverse
from django.utils.functional import lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import RedirectView
from martor.views import markdown_search_user

from judge.feed import AtomBlogFeed, AtomCommentFeed, AtomProblemFeed, BlogFeed, CommentFeed, ProblemFeed
from judge.sitemap import sitemaps
from judge.views import TitledTemplateView, api, blog, comment, contests, language, license, mailgun, organization, \
    preview, problem, problem_manage, ranked_submission, register, stats, status, submission, tag, tasks, ticket, \
    two_factor, user, widgets
from judge.views.problem_data import ProblemDataView, ProblemSubmissionDiff, problem_data_file, problem_init_view
from judge.views.register import ActivationView, RegistrationView
from judge.views.select2 import AssigneeSelect2View, CommentSelect2View, ContestSelect2View, \
    ContestUserSearchSelect2View, OrganizationSelect2View, OrganizationUserSelect2View, ProblemSelect2View, \
    TagGroupSelect2View, TagSelect2View, TicketUserSelect2View, UserSearchSelect2View, UserSelect2View
from judge.views.widgets import martor_image_uploader

SEND_ACTIVATION_EMAIL = getattr(settings, 'SEND_ACTIVATION_EMAIL', True)
REGISTRATION_COMPLETE_TEMPLATE = 'registration/registration_complete.html' if SEND_ACTIVATION_EMAIL \
                                 else 'registration/activation_complete.html'

register_patterns = [
    path('activate/complete/',
         TitledTemplateView.as_view(template_name='registration/activation_complete.html',
                                    title=_('Activation Successful!')),
         name='registration_activation_complete'),
    path('activate/<str:activation_key>/', ActivationView.as_view(), name='registration_activate'),
    path('register/', RegistrationView.as_view(), name='registration_register'),
    path('register/complete/',
         TitledTemplateView.as_view(template_name=REGISTRATION_COMPLETE_TEMPLATE,
                                    title=_('Registration Completed')),
         name='registration_complete'),
    path('register/closed/',
         TitledTemplateView.as_view(template_name='registration/registration_closed.html',
                                    title=_('Registration Not Allowed')),
         name='registration_disallowed'),
    path('login/', user.CustomLoginView.as_view(), name='auth_login'),
    path('logout/', user.UserLogoutView.as_view(), name='auth_logout'),
    path('password/change/', user.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html',
        title=_('Password change successful'),
    ), name='password_change_done'),
    path('password/reset/', user.CustomPasswordResetView.as_view(), name='password_reset'),
    re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
            auth_views.PasswordResetConfirmView.as_view(
                template_name='registration/password_reset_confirm.html',
                title=_('Enter new password'),
            ), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
        title=_('Password reset complete'),
    ), name='password_reset_complete'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
        title=_('Password reset sent'),
    ), name='password_reset_done'),
    path('social/error/', register.social_auth_error, name='social_auth_error'),

    # Two-factor authentication
    path('2fa/', two_factor.TwoFactorLoginView.as_view(), name='login_2fa'),
    path('2fa/enable/', two_factor.TOTPEnableView.as_view(), name='enable_2fa'),
    path('2fa/refresh/', two_factor.TOTPRefreshView.as_view(), name='refresh_2fa'),
    path('2fa/disable/', two_factor.TOTPDisableView.as_view(), name='disable_2fa'),
    path('2fa/webauthn/attest/', two_factor.WebAuthnAttestationView.as_view(), name='webauthn_attest'),
    path('2fa/webauthn/assert/', two_factor.WebAuthnAttestView.as_view(), name='webauthn_assert'),
    path('2fa/webauthn/delete/<int:pk>', two_factor.WebAuthnDeleteView.as_view(), name='webauthn_delete'),
    path('2fa/scratchcode/generate/', user.generate_scratch_codes, name='generate_scratch_codes'),

    # API tokens
    path('api/token/generate/', user.generate_api_token, name='generate_api_token'),
    path('api/token/remove/', user.remove_api_token, name='remove_api_token'),
]


def exception(request):
    if not request.user.is_superuser:
        raise Http404()
    raise RuntimeError('@Xyene asked me to cause this')


def paged_list_view(view, name):
    return include([
        path('', view.as_view(), name=name),
        path('<int:page>/', view.as_view(), name=name),
    ])


urlpatterns = [
    path('', blog.PostList.as_view(template_name='home.html', title=_('Home')), kwargs={'page': 1}, name='home'),
    path('500/', exception),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include(register_patterns)),
    path('', include('social_django.urls', namespace='social')),

    # Problemas
    path('problems', include([
        path('', problem.ProblemList.as_view(), name='problem_list'),
        path('random/', problem.RandomProblem.as_view(), name='problem_random'),
        path('suggest_list/', problem.SuggestList.as_view(), name='problem_suggest_list'),
        path('suggest', problem.ProblemSuggest.as_view(), name='problem_suggest'),
        path('create', problem.ProblemCreate.as_view(), name='problem_create'),
    ])),

    path('problem/<str:problem>', include([
        path('', problem.ProblemDetail.as_view(), name='problem_detail'),
        path('edit', problem.ProblemEdit.as_view(), name='problem_edit'),
        path('editorial', problem.ProblemSolution.as_view(), name='problem_editorial'),
        path('raw', xframe_options_sameorigin(problem.ProblemRaw.as_view()), name='problem_raw'),
        path('pdf', problem.ProblemPdfView.as_view(), name='problem_pdf'),
        path('pdf/<slug:language>', problem.ProblemPdfView.as_view(), name='problem_pdf'),
        path('clone', problem.ProblemClone.as_view(), name='problem_clone'),
        path('submit', problem.ProblemSubmit.as_view(), name='problem_submit'),
        path('resubmit/<int:submission>', problem.ProblemSubmit.as_view(), name='problem_submit'),

        path('rank/', paged_list_view(ranked_submission.RankedSubmissions, 'ranked_submissions')),
        path('submissions/', paged_list_view(submission.ProblemSubmissions, 'chronological_submissions')),
        path('submissions/<str:user>/', paged_list_view(submission.UserProblemSubmissions, 'user_submissions')),

        path('', RedirectView.as_view(pattern_name='problem_detail', permanent=True)),

        path('test_data', ProblemDataView.as_view(), name='problem_data'),
        path('test_data/init', problem_init_view, name='problem_data_init'),
        path('test_data/diff', ProblemSubmissionDiff.as_view(), name='problem_submission_diff'),
        path('data/<path:path>', problem_data_file, name='problem_data_file'),

        path('tickets/', ticket.ProblemTicketListView.as_view(), name='problem_ticket_list'),
        path('tickets/new', ticket.NewProblemTicketView.as_view(), name='new_problem_ticket'),

        path('manage/submission', include([
            path('', problem_manage.ManageProblemSubmissionView.as_view(), name='problem_manage_submissions'),
            path('rejudge', problem_manage.RejudgeSubmissionsView.as_view(), name='problem_submissions_rejudge'),
            path('rejudge/preview', problem_manage.PreviewRejudgeSubmissionsView.as_view(),
                 name='problem_submissions_rejudge_preview'),
            path('rejudge/success/<slug:task_id>', problem_manage.rejudge_success,
                 name='problem_submissions_rejudge_success'),
            path('rescore/all', problem_manage.RescoreAllSubmissionsView.as_view(),
                 name='problem_submissions_rescore_all'),
            path('rescore/success/<slug:task_id>', problem_manage.rescore_success,
                 name='problem_submissions_rescore_success'),
        ])),
    ])),

    # Tags
    path('tags', include([
        path('', tag.TagProblemList.as_view(), name='tagproblem_list'),
        path('create', tag.TagProblemCreate.as_view(), name='tagproblem_create'),
        path('random/', tag.TagRandomProblem.as_view(), name='tagproblem_random'),
        path('find', tag.TagFindProblem.as_view(), name='tagproblem_find'),
    ])),

    path('tag/<str:tagproblem>', include([
        path('', tag.TagProblemDetail.as_view(), name='tagproblem_detail'),
        path('assign', tag.TagProblemAssign.as_view(), name='tagproblem_assign'),
        path('', RedirectView.as_view(pattern_name='tagproblem_detail', permanent=True)),
    ])),

    # Submissions
    path('submissions/', paged_list_view(submission.AllSubmissions, 'all_submissions')),
    path('submissions/diff', submission.SubmissionSourceDiff, name='diff_submissions'),
    path('submissions/user/<str:user>/', paged_list_view(submission.AllUserSubmissions, 'all_user_submissions')),

    path('src/<int:submission>', submission.SubmissionSource.as_view(), name='submission_source'),
    path('src/<int:submission>/raw', submission.SubmissionSourceRaw.as_view(), name='submission_source_raw'),
    path('src/<int:submission>/download', submission.SubmissionSourceDownload.as_view(),
         name='submission_source_download'),

    path('submission/<int:submission>', include([
        path('', submission.SubmissionStatus.as_view(), name='submission_status'),
        path('abort', submission.abort_submission, name='submission_abort'),
    ])),

    # Usuarios
    path('users/', include([
        path('', user.users, name='user_list'),
        path('<int:page>/', lambda request, page:
             HttpResponsePermanentRedirect('%s?page=%s' % (reverse('user_list'), page))),
        path('find', user.user_ranking_redirect, name='user_ranking_redirect'),
    ])),
    path('user', user.UserAboutPage.as_view(), name='user_page'),
    path('edit/profile/', user.edit_profile, name='user_edit_profile'),
    path('data/prepare/', user.UserPrepareData.as_view(), name='user_prepare_data'),
    path('data/download/', user.UserDownloadData.as_view(), name='user_download_data'),
    path('user/<str:user>', include([
        path('', user.UserAboutPage.as_view(), name='user_page'),
        path('ban', user.UserBan.as_view(), name='user_ban'),
        path('blog/', paged_list_view(user.UserBlogPage, 'user_blog')),
        path('comment/', paged_list_view(user.UserCommentPage, 'user_comment')),
        path('solved/', include([
            path('', user.UserProblemsPage.as_view(), name='user_problems'),
            path('ajax', user.UserPerformancePointsAjax.as_view(), name='user_pp_ajax'),
        ])),
        path('submissions/', paged_list_view(submission.AllUserSubmissions, 'all_user_submissions_old')),
        path('', RedirectView.as_view(pattern_name='all_user_submissions', permanent=True)),
    ])),

    # Contests
    path('contests/', paged_list_view(contests.ContestList, 'contest_list')),
    path('contests.ics', contests.ContestICal.as_view(), name='contest_ical'),
    path('contests/<int:year>/<int:month>/', contests.ContestCalendar.as_view(), name='contest_calendar'),
    path('contests/new', contests.CreateContest.as_view(), name='contest_new'),
    re_path(r'^contests/tag/(?P<name>[a-z-]+)', include([
        path('', contests.ContestTagDetail.as_view(), name='contest_tag'),
        path('ajax', contests.ContestTagDetailAjax.as_view(), name='contest_tag_ajax'),
    ])),
    path('contest/<str:contest>', include([
        path('', contests.ContestDetail.as_view(), name='contest_view'),
        path('all', contests.ContestAllProblems.as_view(), name='contest_all_problems'),
        path('edit', contests.EditContest.as_view(), name='contest_edit'),
        path('moss', contests.ContestMossView.as_view(), name='contest_moss'),
        path('moss/delete', contests.ContestMossDelete.as_view(), name='contest_moss_delete'),
        path('announce', contests.ContestAnnounce.as_view(), name='contest_announce'),
        path('clone', contests.ContestClone.as_view(), name='contest_clone'),
        path('ranking/', contests.ContestRanking.as_view(), name='contest_ranking'),
        path('public_ranking/', contests.ContestPublicRanking.as_view(), name='contest_public_ranking'),
        path('official_ranking/', contests.ContestOfficialRanking.as_view(), name='contest_official_ranking'),
        path('register', contests.ContestRegister.as_view(), name='contest_register'),
        path('join', contests.ContestJoin.as_view(), name='contest_join'),
        path('leave', contests.ContestLeave.as_view(), name='contest_leave'),
        path('stats', contests.ContestStats.as_view(), name='contest_stats'),
        path('data/prepare/', contests.ContestPrepareData.as_view(), name='contest_prepare_data'),
        path('data/download/', contests.ContestDownloadData.as_view(), name='contest_download_data'),

        path('rank/<str:problem>/', paged_list_view(ranked_submission.ContestRankedSubmission, 'contest_ranked_submissions')),
        path('submissions/', paged_list_view(submission.AllContestSubmissions, 'contest_all_submissions')),
        path('submissions/<str:user>/', paged_list_view(submission.UserAllContestSubmissions, 'contest_all_user_submissions')),
        path('submissions/<str:user>/<str:problem>/', paged_list_view(submission.UserContestSubmissions, 'contest_user_submissions')),

        path('participations/', contests.ContestParticipationList.as_view(), name='contest_participation_own'),
        path('participations/<str:user>', contests.ContestParticipationList.as_view(), name='contest_participation'),
        path('participation/disqualify', contests.ContestParticipationDisqualify.as_view(), name='contest_participation_disqualify'),

        path('', RedirectView.as_view(pattern_name='contest_view', permanent=True)),
    ])),

    # Organizations
    path('organizations/', organization.OrganizationList.as_view(), name='organization_list'),
    path('organizations/create', organization.CreateOrganization.as_view(), name='organization_create'),
    path('organization/<int:pk>-<slug:slug>', include([
        path('', organization.OrganizationHome.as_view(), name='organization_home'),
        path('users/', organization.OrganizationUsers.as_view(), name='organization_users'),
        path('join', organization.JoinOrganization.as_view(), name='join_organization'),
        path('leave', organization.LeaveOrganization.as_view(), name='leave_organization'),
        path('edit', organization.EditOrganization.as_view(), name='edit_organization'),
        path('kick', organization.KickUserWidgetView.as_view(), name='organization_user_kick'),
        path('problems/', organization.ProblemListOrganization.as_view(), name='problem_list_organization'),
        path('contests/', organization.ContestListOrganization.as_view(), name='contest_list_organization'),
        path('submissions/', paged_list_view(organization.SubmissionListOrganization, 'submission_list_organization')),
        path('problem-create', organization.ProblemCreateOrganization.as_view(), name='problem_create_organization'),
        path('contest-create', organization.ContestCreateOrganization.as_view(), name='contest_create_organization'),

        path('request', organization.RequestJoinOrganization.as_view(), name='request_organization'),
        path('request/<int:rpk>', organization.OrganizationRequestDetail.as_view(), name='request_organization_detail'),
        path('requests/', include([
            path('pending', organization.OrganizationRequestView.as_view(), name='organization_requests_pending'),
            path('log', organization.OrganizationRequestLog.as_view(), name='organization_requests_log'),
            path('approved', organization.OrganizationRequestLog.as_view(states=('A',), tab='approved'),
                 name='organization_requests_approved'),
            path('rejected', organization.OrganizationRequestLog.as_view(states=('R',), tab='rejected'),
                 name='organization_requests_rejected'),
        ])),

        path('post/', include([
            path('new', organization.BlogPostCreateOrganization.as_view(), name='blog_post_create_organization'),
        ])),

        path('', RedirectView.as_view(pattern_name='organization_home', permanent=True)),
    ])),

    # Runtimes & Status
    path('runtimes/', language.LanguageList.as_view(), name='runtime_list'),
    path('runtimes/matrix/', status.version_matrix, name='version_matrix'),
    path('status/', status.status_all, name='status_all'),
    path('status/oj/', status.status_oj, name='status_oj'),

    # API v2
    path('api/v2/', include([
        path('contests', api.api_v2.APIContestList.as_view()),
        path('contest/<str:contest>', api.api_v2.APIContestDetail.as_view()),
        path('problems', api.api_v2.APIProblemList.as_view()),
        path('problem/<str:problem>', api.api_v2.APIProblemDetail.as_view()),
        path('users', api.api_v2.APIUserList.as_view()),
        path('user/<str:user>', api.api_v2.APIUserDetail.as_view()),
        path('submissions', api.api_v2.APISubmissionList.as_view()),
        path('submission/<int:submission>', api.api_v2.APISubmissionDetail.as_view()),
        path('organizations', api.api_v2.APIOrganizationList.as_view()),
        path('participations', api.api_v2.APIContestParticipationList.as_view()),
        path('languages', api.api_v2.APILanguageList.as_view()),
        path('judges', api.api_v2.APIJudgeList.as_view()),
    ])),

    # Blog
    path('posts/', paged_list_view(blog.PostList, 'blog_post_list')),
    path('posts/new', blog.BlogPostCreate.as_view(), name='blog_post_create'),
    path('posts/<str:slug>', include([
        path('', blog.BlogPostDetail.as_view(), name='blog_post_detail'),
        path('edit', blog.BlogPostEdit.as_view(), name='blog_post_edit'),
        path('delete', blog.BlogPostDelete.as_view(), name='blog_post_delete'),
        path('comment', comment.NewComment.as_view(), name='blog_post_comment'),
        path('', RedirectView.as_view(pattern_name='blog_post_detail', permanent=True)),
    ])),

    # Feeds
    path('feeds/problems/', ProblemFeed(), name='problem_feed'),
    path('feeds/blog/', BlogFeed(), name='blog_feed'),
    path('feeds/comments/', CommentFeed(), name='comment_feed'),
    path('feeds/problems/atom/', AtomProblemFeed(), name='problem_feed_atom'),
    path('feeds/blog/atom/', AtomBlogFeed(), name='blog_feed_atom'),
    path('feeds/comments/atom/', AtomCommentFeed(), name='comment_feed_atom'),

    # Tasks
    path('tasks/', include([
        path('', tasks.TaskList.as_view(), name='task_list'),
        path('<slug:task_id>', tasks.TaskDetail.as_view(), name='task_detail'),
    ])),

    # Widgets
    path('widget/martor_image_upload', martor_image_uploader, name='martor_image_upload'),
    path('widget/assignee', AssigneeSelect2View.as_view(), name='widget_assignee'),
    path('widget/comment', CommentSelect2View.as_view(), name='widget_comment'),
    path('widget/contest', ContestSelect2View.as_view(), name='widget_contest'),
    path('widget/contest_user_search', ContestUserSearchSelect2View.as_view(), name='widget_contest_user_search'),
    path('widget/organization', OrganizationSelect2View.as_view(), name='widget_organization'),
    path('widget/organization_user', OrganizationUserSelect2View.as_view(), name='widget_organization_user'),
    path('widget/problem', ProblemSelect2View.as_view(), name='widget_problem'),
    path('widget/tag_group', TagGroupSelect2View.as_view(), name='widget_tag_group'),
    path('widget/tag', TagSelect2View.as_view(), name='widget_tag'),
    path('widget/ticket_user', TicketUserSelect2View.as_view(), name='widget_ticket_user'),
    path('widget/user_search', UserSearchSelect2View.as_view(), name='widget_user_search'),
    path('widget/user', UserSelect2View.as_view(), name='widget_user'),
])

# Favicons
favicon_paths = [
    'apple-touch-icon-180x180.png', 'apple-touch-icon-114x114.png', 'android-chrome-72x72.png',
    'apple-touch-icon-57x57.png', 'apple-touch-icon-72x72.png', 'apple-touch-icon.png', 'mstile-70x70.png',
    'android-chrome-36x36.png', 'apple-touch-icon-precomposed.png', 'apple-touch-icon-76x76.png',
    'apple-touch-icon-60x60.png', 'android-chrome-96x96.png', 'mstile-144x144.png', 'mstile-150x150.png',
    'safari-pinned-tab.svg', 'android-chrome-144x144.png', 'apple-touch-icon-152x152.png',
    'favicon-96x96.png', 'favicon-32x32.png', 'favicon-16x16.png', 'android-chrome-192x192.png',
    'android-chrome-48x48.png', 'mstile-310x150.png', 'apple-touch-icon-144x144.png',
    'browserconfig.xml', 'manifest.json', 'apple-touch-icon-120x120.png', 'mstile-310x310.png'
]

static_lazy = lazy(static, str)
for favicon in favicon_paths:
    urlpatterns.append(path(favicon, RedirectView.as_view(url=static_lazy('icons/' + favicon))))

# Handlers
handler404 = 'judge.views.error.error404'
handler403 = 'judge.views.error.error403'
handler500 = 'judge.views.error.error500'

# Local overrides
try:
    import local_urls
except ImportError:
    pass
