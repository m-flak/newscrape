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
