$(document).ready(function() {
    $('#single').hide();
      $('#summernote').summernote({
        placeholder: 'Hello stand alone ui',
        tabsize: 2,
        height: 120,
        toolbar: [
          ['style', ['style']],
          ['font', ['bold', 'underline', 'clear']],
          ['color', ['color']],
          ['para', ['ul', 'ol', 'paragraph']],
          ['table', ['table']],
          ['insert', ['link', 'picture', 'video']],
          ['view', ['fullscreen', 'codeview', 'help']]
        ]
      });

        var selected = $('#picker').val();
        if (selected === 'select') {
          $('#single').prop('required', true).show();
        }

      $("#picker").change(function () {
        var selected_option = $('#picker').val();
      
        if (selected_option === 'select') {
          $('#single').prop('required', true).show();
        }
        if (selected_option != 'select') {
          $("#single").prop('required', false).hide();
        }
      })
});