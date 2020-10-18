'''webauth Signals'''

# pylint: disable=unused-argument
def clean_save(sender, instance, **kwargs):
    '''Validate the User model.'''
    instance.full_clean()
