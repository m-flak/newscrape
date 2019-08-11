$(function() {
  if ($("div.news-story").length > 0) {
    $("a.delete-story").on("click", function(e) {
      let news_story = $(e.currentTarget.parentElement);
      var id = news_story.data('storyid');
      var dum = 'dummy';

      $.ajax({
        method: "POST",
        url: create_api_url("saved_stories"),
        data: { action: 'delete', id: id, link: dum, headline: dum,
                summary: dum
              }
      }).done(function(d) {
        if (d.status !== "FAIL") {
          news_story.remove();
        }
      });
    });
  }
});
