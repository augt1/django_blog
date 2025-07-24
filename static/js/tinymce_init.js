tinymce.init({
  width: 600,
  selector: 'textarea#id_content',
  plugins:
    'anchor autolink charmap codesample emoticons image link lists media searchreplace table visualblocks wordcount',
  toolbar:
    'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table | align lineheight | numlist bullist indent outdent | emoticons charmap | removeformat',
  content_css: 'dark',
  skin: 'oxide-dark',
})
