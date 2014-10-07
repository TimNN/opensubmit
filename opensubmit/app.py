from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def ensure_user_groups(sender,instance, signal, created, **kwargs):
    """
        Make sure that all neccessary user groups exist and have the right permissions,
        directly after the auth system was installed. We detect this by waiting for the admin 
        account creation.
        The permission objects were already generated by the Django database initialization.
    """
    if not (instance.is_superuser and created):
        return

    print "Creating OpenSubmit user roles."

    from django.contrib.auth.models import Group, Permission

    tutor_perms = "add_submission", "change_submission", "delete_submission", "add_submissionfile", "change_submissionfile", "delete_submissionfile"
    owner_perms = "add_assignment", "add_grading", "add_gradingscheme", "add_submission", "add_submissionfile", "change_assignment", "change_course", "change_grading", "change_gradingscheme", "change_submission", "change_submissionfile", "delete_assignment", "delete_grading", "delete_gradingscheme", "delete_submission", "delete_submissionfile",

    tutor_group, created = Group.objects.get_or_create(name="Student Tutors")
    if created:
        tutor_group.permissions = [Permission.objects.get(codename=perm) for perm in tutor_perms]      
        tutor_group.save()  

    owner_group, created = Group.objects.get_or_create(name="Course Owners")
    if created:
        owner_group.permissions = [Permission.objects.get(codename=perm) for perm in owner_perms]
        owner_group.save()


# Give human readable names to apps in the Django admin view
class OpenSubmitConfig(AppConfig):
    name = 'opensubmit'
    verbose_name = "Teacher Backend"