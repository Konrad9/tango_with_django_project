$(document).ready(function() {

    $('#like_btn').click(function() {
        var categoryIdVar;
        categoryIdVar = $(this).attr('data-categoryid');
        
        $.get('/rango/like_category/',
            {'category_id': categoryIdVar},
            function(data) {
                $('#like_count').html(data);
                $('#like_btn').hide();
            })
    });
    
    $('#search-input').keyup(function() {
        var query;
        query = $(this).val();
        
        $.get('/rango/suggest/',
        {'suggestion': query},
        function(data) {
            $('#categories-listing').html(data);
        })
    });
    
    $('.rango-add-page').click(function() {
        var categoryId = $(this).attr('data-categoryid');
        var title = $(this).attr('data-title');
        var url = $(this).attr('data-url');
        var clickedButton = $(this);
        
        $.get('/rango/search_add_page/',
            {'category_id': categoryId,
            'title':title,
            'url':url},
            function(data) {
                $('#page-listing').html(data);
                clickedButton.hide();
            })
    });
    
});