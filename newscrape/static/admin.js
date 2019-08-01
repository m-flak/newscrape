$(function() {
  var field_selectors = [];

  let username_labels = $("label[for|='user_details']").filter(function() {
    if (this.parentElement.tagName.match(/li/i) != null) {
      return true;
    }
    return false;
  });
  /* generate selectors for fields with the account names */
  username_labels.each(function() {
    field_selectors.push(function(a) {
      return "input[name|='" + a + "']";
    }($(this).attr('for')));
  });
  /* turn the username labels into just that */
  /* Length of field_selectors == length of username_labels */
  for (var i = 0; i < field_selectors.length; i++) {
    username_labels.text(function(index, string) {
      if (i == index) {
        return $(field_selectors[i]).val();
      }
      return string;
    });
  }
  /* style them */
  username_labels.css('font-weight', 'bold');
  username_labels.css('text-decoration', 'underline');
  /* visually tweak password fields */
  $("input[type=password]").val('defaultpassword');
});
