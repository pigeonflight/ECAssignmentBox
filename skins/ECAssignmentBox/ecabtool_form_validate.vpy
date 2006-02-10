## Script (Python) "ecabtool_form_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##
REQUEST = context.REQUEST

# resourcestrings
I18N_DOMAIN = 'eduComponents'

errors = {}

student_id_attr = REQUEST.get('student_id_attr', None)
major_attr = REQUEST.get('major_attr', None)

if student_id_attr is not None:
    # strips the id, so make sure we test the stripped version
    student_id_attr = student_id_attr.strip() 
    REQUEST.set('student_id_attr', student_id_attr)

student_id_attr_error = context.check_id(student_id_attr, 0, None)

if student_id_attr_error:
    state.setError('error_student_id_attr', student_id_attr_error, new_status='failure')


# FIXME: add validation for major_attr

if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state