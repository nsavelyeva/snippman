      $(function() {

        $("onLoad", function() {

          $.getJSON("/_statistics", {}, function(data) {
            languages = data.result
            content = '<ul class="list-group">'
            snippets_count = 0
            languages_count = 0
            for (i = 0; i < languages.length; i++) {
                if (languages[i][1] > 0) {
                    snippets_count += languages[i][1]
                    languages_count += 1
                    content += '<li class="list-group-item"><a href="/snippets/' + languages[i][0] + '">' + languages[i][0] + '</a> <span class="badge">' + languages[i][1] +'</span></li>';
                }
            }
            if (languages.length == 0) {content = 'No snippets found'}
            else {content += '</ul>'}
            content = '<li class="list-group-item">Total snippets: <span class="badge">' + snippets_count + '</span></li>' +
                      '<li class="list-group-item">Total languages: <span class="badge">' + languages_count + '</span></li>' +
                      '<li class="list-group-item">Snippets per language:<br>' + content + '</li></ul>'
            $("#statistics").html(content);
          });  // getJSON

          $.getJSON("/_pop1_max_visits", {}, function(data) {
            content = '<h4 class="list-group-item-heading">Most Popular Snippet</h4>'
            if (data.visits) {
                content += '<a href="/snippets/view/' + data.id + '">' + data.description + '</a><br>(visits: ' + data.visits + ')'
            } else {content += 'No snippets visited'}
            $("#pop-1").html(content);
          });  // getJSON

          $.getJSON("/_new1_last_created", {}, function(data) {
            content = '<h4 class="list-group-item-heading">The Youngest Snippet</h4>'
            if (data.created) {
                if(data.created.indexOf('.') >= 0) {
                    created = data.created.substring(0, data.created.indexOf("."))
                } else created = data.created
                content += '<a href="/snippets/view/' + data.id + '">' + data.description + '</a><br>(created: ' + created + ')'
            } else {content += 'No snippets created'}
            $("#new-1").html(content);
          });  // getJSON

          $.getJSON("/_fresh1_last_modified", {}, function(data) {
            content = '<h4 class="list-group-item-heading">The Freshest Snippet</h4>'
            if (data.modified) {
                if (data.modified.indexOf('.') >= 0) {
                    modified = data.modified.substring(0, data.modified.indexOf("."))
                } else modified = data.modified
                content += '<a href="/snippets/view/' + data.id + '">' + data.description + '</a><br>(updated: ' + modified + ')'
            } else {content += 'No snippets updated'}
                $("#fresh-1").html(content);
          });  // getJSON

          return false;
        });  // onLoad function()

      });  // function()

      function show_snippet(snippet_id) {

          $.getJSON("/_snippet_body", {"snippet_id": snippet_id}, function(data) {
            content = $("#snippet-" + data.id).html()
            highlight = false
            if (content == '') {
                if (data.snippet) {
                    content += '<pre><code>' + data.snippet + '</code></pre>'
                    highlight = true
                } else {content += 'No snippet details found'}
            } else {content = ''}
            $("#snippet-" + data.id).html(content);
            if (highlight == true) {
                $("#snippet-" + data.id).each(function(i, block) {
                    hljs.highlightBlock(block);
                });
            } else {
                $("#snippet-" + data.id).removeClass(function() {
                    return $(this).attr("class");
                });
            }
          });  // getJSON
      } // show_snippet()
