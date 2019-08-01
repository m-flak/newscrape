from flask_wtf import FlaskForm
import wtforms
from wtforms import (
StringField, HiddenField, SubmitField, FieldList, FormField, BooleanField,
PasswordField
)
from wtforms.validators import DataRequired, Email, EqualTo
import newscrape as ns

#
### ADMIN PANEL FORMS
#
class AdminUsersDetails(wtforms.Form):
    old_name = HiddenField(validators=[DataRequired()])
    new_name = StringField("Username", validators=[DataRequired()])
    old_email = HiddenField(validators=[DataRequired(), Email()])
    new_email = StringField("Email",validators=[DataRequired(), Email()])
    password  = PasswordField("Pass", default='defaultpassword')
    is_admin  = BooleanField("Admin?",false_values=(False,'false',0,'0'))
    update_user = BooleanField("Update?",default=False,false_values=(False,'false',0,'0'))

    def update_password(self, pw):
        if len(pw) == 0 or 'defaultpassword' in pw:
            return
        user = ns.models.User.query.filter_by(name=self.old_name.data).first()
        if user is not None:
            user.change_password(pw)

    def update_changed(self):
        # Update password (if changed)
        self.update_password(self.password.data)
        # Update Admin Field
        ns.models.User.query.filter_by(name=self.old_name.data).\
            filter(ns.models.User.admin != self.is_admin.data).\
            update({'admin': self.is_admin.data,}, synchronize_session=False)
        # Update Username
        if self.new_name.data != self.old_name.data:
            ns.models.User.query.filter_by(name=self.old_name.data).\
                update({'name': self.new_name.data,}, synchronize_session=False)
        # Update Email
        if self.new_email.data != self.old_email.data:
            ns.models.User.query.filter_by(email=self.old_email.data).\
                update({'email': self.new_email.data,}, synchronize_session=False)

        ns.db.session.commit()

class AdminUsers(FlaskForm):
    user_details = FieldList(FormField(AdminUsersDetails))
    submit = SubmitField("Update Users")

#
### USER PANEL FORMS
#
class UserUpdatePassword(FlaskForm):
    cur_pass  = PasswordField("Current Password", validators=[DataRequired()])
    new_pass  = PasswordField("New     Password", validators=[DataRequired()])
    new_pass2 = PasswordField("Confirm Password", validators=[DataRequired(),
                                                    EqualTo('new_pass')])
    submit    = SubmitField()

#######################################################

# Generator for `AdminUsersDetails`, pass to append_entry()
def admin_user_details(num_users):
    info = ns.models.User.query.with_entities(ns.models.User.name,
                ns.models.User.email, ns.models.User.admin)
    for i in range(0, num_users):
        yield dict({
            'old_name': info[i][0],
            'new_name': info[i][0],
            'old_email': info[i][1],
            'new_email': info[i][1],
            'is_admin': info[i][2],
        })
