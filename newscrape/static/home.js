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

/* Create an unique identifier for a given news story search result */
function make_story_identifier(story) {
  var lead = new Uint8Array([story.link.length>255?255:story.link.length,
                            story.headline.length>255?255:story.headline.length,
                            story.summary.length>255?255:story.summary.length]);
  let field_id = function mkid(base_str, itr, offset, obj) {
    if (itr == 4) {
      return base_str;
    }
    var hexxy = obj.charCodeAt(offset+itr)<<8|obj.charCodeAt(offset+itr+1);
    return mkid(base_str.concat(hexxy.toString(16)), itr+2, offset, obj);
  };
  var link_id = field_id('',0,12,story.link);
  var head_id = field_id('',0,7,story.headline);
  var sum_id  = field_id('',0,5,story.summary);

  return("ax-by-cz".replace(/[axbycz]/g, function(m) {
    switch(m) {
      case 'a':
        return lead[0].toString(16);
      break;
      case 'x':
        return link_id;
      break;
      case 'b':
        return lead[1].toString(16);
      break;
      case 'y':
        return head_id;
      break;
      case 'c':
        return lead[2].toString(16);
      break;
      case 'z':
        return sum_id;
      default:
        return '';
      break;
    }
  }));
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
    }).done(function(d) {
      if (d.status === "FAIL") {
        $("div#status-flash").append("Internal Server Error.<br/>");
      }
    });
  });
}

function onclick_delete(e) {
  let keyword = $(e.currentTarget.parentElement.children).filter("p");
  var kw_index  = Number(keyword.parent().attr('id').match(/-(\d+)$/)[1]);
  var kw_text   = keyword.text();

  $("div.keywords").children("div:not(#keyword-new)").each(function(i) {
    /* compare indices starting from 1 rather than 0 */
    if (kw_index == ++i) {
      $(this).remove();
      /* re-index all remaining keywords */
      let all_keywords = $("div.keywords").children("div:not(#keyword-new)");
      for (var j = 0; j < all_keywords.length; j++) {
        all_keywords[j].id = `keyword-${++j}`;
      }
    }
  });

  /* unpushed new keywords require nothing further */
  if (kw_text === "new keyword") {
    return;
  }

  $.ajax({
    method: "POST",
    url: create_api_url("keywords"),
    data: { action: 'delete', keyword: kw_text, value: kw_text }
  }).done(function(d) {
    if (d.status === "FAIL") {
      $("div#status-flash").append("Internal Server Error.<br/>");
    }
  });
}

const saved_story_ids = function() {
  var ssids = new Array();
  $.ajax({
    method: "GET",
    url: create_api_url("saved_stories").concat("&what=id"),
    async: false
  }).done(function(d) {
    if (d.status !== "FAIL") {
      for (var i in d.data) {
        ssids.push(d.data[i]);
      }
    }
  });
  return ssids;
}();

$(function() {
  let engine_prefs = $("form[name='search-engine-prefs']").children().children("input:checkbox");

  /* Update to cookies to user's chosen choices */
  engine_prefs.on("click", function(e) {
    var new_sprefs = new Array();
    engine_prefs.each(function(i,e) {
      if (e.checked) {
        new_sprefs.push($(this).attr('name'));
      }
    });
    if (Cookies.get('newscrape_sprefs') != null) {
      Cookies.remove('newscrape_sprefs');
    }
    Cookies.set('newscrape_sprefs', new_sprefs.toString());
  });

  /* Create default user choices cookie; Otherwise, load them */
  if (Cookies.get('newscrape_sprefs') == null) {
    Cookies.set('newscrape_sprefs', 'google,bing');
  } else {
    var engines = Cookies.get('newscrape_sprefs').split(',');
    for (var i in engines) {
      engine_prefs.each(function() {
        if ($(this).attr('name') === engines[i]) {
          $(this).attr('checked', true);
        }
      });
    }
  }

  $("a.new-keyword").on("click", function(e) {
    var index_new = $("div[id|='keyword']").length;

    $(this).parent().before(`<div id='keyword-${index_new}'><p>new keyword</p>
    <a class='kw modify-keyword' id='modify-keyword-${index_new}' href='#'></a>
    <a class='kw del-keyword' id='del-keyword-${index_new}' href='#'></a>
    </div>`);

    let created_modify = $(`a[id='modify-keyword-${index_new}']`);
    let created_delete = $(`a[id='del-keyword-${index_new}']`);
    add_tooltip(created_modify, "Update Keyword");
    add_tooltip(created_delete, "Delete Keyword");
    created_modify.on("click", onclick_modify);
    created_modify.trigger('click');
    created_delete.on("click", onclick_delete);
  });

  add_tooltip("a.modify-keyword", "Update Keyword");
  add_tooltip("a.del-keyword", "Delete Keyword");
  $("a.modify-keyword").on("click", onclick_modify);
  $("a.del-keyword").on("click", onclick_delete);

  /* Fetch our news stories */
  $.ajax({
    method: "GET",
    url: create_api_url("stories")
  }).done(function(d) {
    if (d.status !== "FAIL") {
      $("div.loading").remove();
    } else {
      return;
    }
    for (var i in d.data) {
      let story = d.data[i];
      var ident = make_story_identifier(story);

      /* only display the save icon if the user hasn't saved the story */
      if (!saved_story_ids.includes(ident)) {
        $("div.results").append(`<div class='news-story' data-storyid='${ident}'>
        <a class='save-story' href='#' title='Save Story'></a>
        <a href='${story.link}'>${story.headline}</a>
        <p>${story.summary}</p></div>`);
      } else {
        $("div.results").append(`<div class='news-story' data-storyid='${ident}'>
        <a href='${story.link}'>${story.headline}</a>
        <p>${story.summary}</p></div>`);
      }
    }

    $("a.save-story").on("click", function(e) {
      let parent = $(e.currentTarget.parentElement);
      var story_id = e.currentTarget.parentElement.dataset.storyid;
      var story_lnk = parent.children("a:not(.save-story)").attr('href');
      var story_hdl = parent.children("a:not(.save-story)").text();
      var story_sum = parent.children("p").text();

      $.ajax({
        method: "POST",
        url: create_api_url("saved_stories"),
        data: { action: 'save', id: story_id, link: Base64.encodeURI(story_lnk),
                headline: Base64.encodeURI(story_hdl),
                summary: Base64.encodeURI(story_sum)
              }
      });
      $(this).remove();
    });
  });

});
