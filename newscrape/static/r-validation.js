var invalidInputs = {
  email: false,
  name: false,
  pass: false
};
function inputs_invalid() {
  return invalidInputs.email | invalidInputs.name | invalidInputs.pass;
}
/** be sure to set `input_sel_prefix` depending on whether we're login or
 ** registration form **/
function inputs_empty() {
  var selector = "input[id|='replaceme']";
  if (typeof input_sel_prefix === 'undefined' || input_sel_prefix == null) {
    throw "input_sel_prefix string var hasn't been set by user";
  }
  else {
    selector = selector.replace(/replaceme/gi, input_sel_prefix);
  }

  let inputs = $(selector);
  for (var i = 0; i < inputs.length; i++) {
    if (inputs[i].value.length == 0) {
      return true;
    }
  }
  return false;
}

$(function() {
  $("form").on("submit", function(e) {
    if (inputs_empty() || inputs_invalid()) {
      alert("You have incorrectly filled out the form.");
      e.preventDefault();
      return;
    }
    /* prepare pw for server */
    let password = $("input[type='password']").prop("value");
    $("input[type='hidden'][name='pass']").val(Base64.encode(password).toString());
  });
  $("input").on("input", function(e) {
    var re = /((?!\)|'|;|!|\||\\|,).)/g; // illegal char regex
    var re2 = /\w+@\w+\.\w+/g;          // email regex

    /* Validate e-mail address */
    try {
      if (e.currentTarget.id.indexOf("email") != -1) {
        if(!e.currentTarget.value.match(re2)) {
          $("#email-invalid")[0].hidden = false;
          invalidInputs.email = true;
        } else {
          $("#email-invalid")[0].hidden = true;
          invalidInputs.email = false;
        }
      }
    } catch(ex) {
      //ignore
    }
    /* Do checks for illegal characters */
    try {
      if (e.currentTarget.value.match(re).length < e.currentTarget.value.length) {
        if(e.currentTarget.id.indexOf("email") != -1) {
          $("#email-invalid")[0].hidden = false;
          invalidInputs.email = true;
        } else if (e.currentTarget.id.indexOf("name") != -1) {
          $("#name-invalid")[0].hidden = false;
          invalidInputs.name = true;
        } else if (e.currentTarget.id.indexOf("password") != -1) {
          $("#password-invalid")[0].hidden = false;
          invalidInputs.pass = true;
        }
      } else {
        if(e.currentTarget.id.indexOf("email") != -1) {
          $("#email-invalid")[0].hidden = true;
          invalidInputs.email = false;
        } else if (e.currentTarget.id.indexOf("name") != -1) {
          $("#name-invalid")[0].hidden = true;
          invalidInputs.name = false;
        } else if (e.currentTarget.id.indexOf("password") != -1) {
          $("#password-invalid")[0].hidden = true;
          invalidInputs.pass = false;
        }
      }
    } catch(ex) {
      //ignore
    }
  });
});
