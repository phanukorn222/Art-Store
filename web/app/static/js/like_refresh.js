$(document).ready(() => {
    $("body").on("click", '.heart-btn-card', function(){
        $(this).closest("form").submit();
    });

    $("body").on("submit", '.like-form', function (e) { 
        e.preventDefault();
        const searchParams = new URLSearchParams(window.location.search)
        const page = searchParams.get('page')
        const action = $(this).attr('action')
        const formData = $(this).serialize()
        $.post(`${action}?page=${page}`, formData, (data) => {
            $("#favourite-arts").html(data?.template)
            if (data?.page !== 0){
                searchParams.set('page', data?.page);
                const newUrl = window.location.origin + window.location.pathname + '?' + searchParams.toString();
                window.history.pushState({ path:newUrl }, '' , newUrl);
            }
        });
    });
});