function get_api_key() {
  var api_tag = null;
  for (var c in document.head.children) {
    var child = document.head.children[c];
    for (var a in child.attributes) {
      var attrib = child.attributes[a];
      if (attrib.name === 'itemprop' && attrib.value === 'user-api-key') {
        api_tag = child;
        break;
      }
    }
    if (api_tag != null) {
      break;
    }
  }
  return api_tag.content;
}

function create_api_url(what_api) {
  var base_url = window.frames.location.href.match(/^.+\//).toString();
  var api_key  = get_api_key();
  return `${base_url}api/${what_api}?api=${api_key}`;
}

function add_tooltip(obj_or_sel, tooltip) {
  if (typeof obj_or_sel === 'string') {
    $(obj_or_sel).attr('title', tooltip);
  } else if (typeof obj_or_sel === 'object') {
    /* assume jquery object if not an element */
    if (!(obj_or_sel instanceof HTMLElement)) {
      obj_or_sel.attr('title', tooltip);
    } else {
      obj_or_sel.title = tooltip;
    }
  }
}

function onclick_modify(e) {
  let keyword = $(e.currentTarget.parentElement.children).filter("p");
  var parent_id = keyword.parent().attr('id');
  var kw_text   = keyword.text();

  /* Replace the keyword text with an input field.
   * If it has already been replaced, do the opposite.
   */
  if ($(`input[name='${parent_id}']`).length == 0) {
    keyword.css('display', 'none');
    keyword.after(`<input name='${parent_id}' type='text' value='${kw_text}' />`);
  } else {
    $(`input[name='${parent_id}']`).trigger('change');
  }

  /* Remove the input field once the user has changed it */
  $(`input[name='${parent_id}']`).on("change", function(e) {
    var post_keyword;

    $(this).css('display', 'none');
    keyword.text($(this).val());
    keyword.css('display', 'inherit');
    $(this).remove();

    if (kw_text === "new keyword") {
      post_keyword = keyword.text();
    } else {
      post_keyword = kw_text;
    }

    $.ajax({
      method: "POST",
      url: create_api_url("keywords"),
      data: { action: 'update', keyword: post_keyword, value: keyword.text() }
    });
  });
}

$(function() {
  $("a.new-keyword").on("click", function(e) {
    var index_new = $("div[id|='keyword']").length;

    $(this).parent().before(`<div id='keyword-${index_new}'><p>new keyword</p>
    <a class='kw modify-keyword' id='modify-keyword-${index_new}' href='#'></a>
    </div>`);

    let created_modify = $(`a[id='modify-keyword-${index_new}']`);
    add_tooltip(created_modify, "Update Keyword");
    created_modify.on("click", onclick_modify);
    created_modify.trigger('click');
  });

  add_tooltip("a.modify-keyword", "Update Keyword");
  $("a.modify-keyword").on("click", onclick_modify);
});
