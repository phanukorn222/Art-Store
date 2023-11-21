$(document).ready(() => {
    $("body").on("click", '.heart-btn-card', function(){
        $(this).closest("form").submit();
    });

    $("body").on("submit", '.like-form', function (e) { 
        e.preventDefault();
        const url = $(this).attr('action')
        const formData = $(this).serialize()
        $.post(url, formData, (data) => {
            $("#count_favourite").html(`${data?.count} favourites`)
            $(this).find('a').first().toggleClass('heart-active').children().toggleClass('bi-heart bi-heart-fill')
        });
    });
});