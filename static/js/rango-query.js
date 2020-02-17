$(document).ready(function() {
    
    $('#about-btn').click(function() {
        msgStr = $('#msg').html();
        msgStr = msgStr + ' ooo, fancy!';
        
        $('#msg').html(msgStr);
    });
    
    $('p').hover(
        function() {    /* executed when hovering over something */
            $(this).css('color', 'red');
        },
        function() {    /* executed when leaving something (after hovering) */
            $(this).css('color', 'black');
    });
    
});