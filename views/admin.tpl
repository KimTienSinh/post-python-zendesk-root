<html><body>
  <style type="text/css">
    body {
        padding:20px;
        margin:10px;
        font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
        font-size:13px;
    }
    input {
        margin-bottom: 10px;
    }
  </style>

  <h3>Community Channel</h3>
  <form method="post" action="/channels/community/settings">
    <div class="form-group">
      <label for="topic_id_field">Topic ID</label><br>
      <input type="text" id="topic_id_field" name="topic_id" value="{{data['topic_id']}}"><br>
      <input type="hidden" name="name" value="{{data['name']}}">
      <input type="hidden" name="return_url" value="{{data['return_url']}}">
      <input type="submit" value="Save" style="font-size:110%;">
    </div>
  </form>
</body></html>