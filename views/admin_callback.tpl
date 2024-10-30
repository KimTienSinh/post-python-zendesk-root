<html><body>
<form id="finish" method="post" action="{{data['return_url']}}">
    <input type="hidden" name="name" value="{{data['name']}}">
    <input type="hidden" name="metadata" value="{{data['metadata']}}">
</form>

<script type="text/javascript">
  // post the form
  var form = document.forms['finish'];
  form.submit();
</script>
</body></html>