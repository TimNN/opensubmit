'''
    Test cases for tutor 'GET' views and actions.
'''

from opensubmit.tests.cases import SubmitTutorTestCase
from opensubmit.models import SubmissionFile, Assignment, Submission
from django.contrib.admin.sites import AdminSite
from django.core.files import File

class TutorTestCaseSet():
    def testTeacherDashboardView(self):
        response=self.c.get('/teacher/')
        self.assertEquals(response.status_code, 200)

    def testAssignmentListBackend(self):
        from opensubmit.admin.assignment import AssignmentAdmin
        from opensubmit.admin.assignment import course as course_title
        assadm = AssignmentAdmin(Assignment, AdminSite())
        assignments_shown = assadm.get_queryset(self.request)
        for assignment in assignments_shown:
            self.assertIn(assignment.course, self.all_courses)

    def testSubmissionListView(self):
        response=self.c.get('/teacher/opensubmit/submission/')
        self.assertEquals(response.status_code, 200)

    def testSubmissionEditView(self):
        sub = self.createValidatedSubmission(self.current_user)
        response=self.c.get('/teacher/opensubmit/submission/%u/change/'%sub.pk)
        self.assertEquals(response.status_code, 200)

    def testGradingTableView(self):
        response=self.c.get('/course/%u/gradingtable/'%self.course.pk)
        self.assertEquals(response.status_code, 200)

    def testDuplicateReportView(self):
        # Using this method twice generates a duplicate upload
        sub1 = self.createValidatableSubmission(self.enrolled_students[0])
        sub2 = self.createValidatableSubmission(self.enrolled_students[1])
        sub3 = self.createValidatableSubmission(self.enrolled_students[2])
        sub3.state=Submission.WITHDRAWN
        sub3.save()
        response=self.c.get('/assignments/%u/duplicates/'%self.validatedAssignment.pk)
        self.assertEquals(response.status_code, 200)
        # expect both submissions to be in the report
        self.assertIn('#%u'%sub1.pk, str(response))
        self.assertIn('#%u'%sub2.pk, str(response))
        # expect withdrawn submissions to be left out
        self.assertNotIn('#%u'%sub3.pk, str(response))

    def testPreviewView(self):
        sub1 = self.createValidatedSubmission(self.current_user)
        response=self.c.get('/preview/%u/'%sub1.pk)
        self.assertEquals(response.status_code, 200)

    def testPreviewBrokenView(self):
        '''
            Test proper handling of archives containing files with invalid unicode.
        '''
        sub1 = self.createValidatedSubmission(self.current_user)
        for fname in [u'broken_preview.gz', u'broken_preview2.gz', u'broken_preview.zip']:
            subfile = self.createSubmissionFile("/opensubmit/tests/submfiles/"+fname)
            sub1.file_upload=subfile
            sub1.save()
            response=self.c.get('/preview/%u/'%sub1.pk)
            self.assertEquals(response.status_code, 200)

class TutorTestCase(SubmitTutorTestCase, TutorTestCaseSet):
    '''
        Run the tests from the tutor case set as student tutor.
    '''
    def testCannotUseAdminBackend(self):
        '''
            Not in the test set above that is inherited for teacher and admin tests.
        '''
        response = self.c.get('/admin/auth/user/')
        self.assertEquals(response.status_code, 403)        # 302: can access the model in principle, 403: can never access the app label
