$(function() {
    
    // Shameless taken from the docs, to allow for same page bidding
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            function sameOrigin(url) {
                // test that a given url is a same-origin URL
                // url could be relative or scheme relative or absolute
                var host = document.location.host; // host + port
                var protocol = document.location.protocol;
                var sr_origin = '//' + host;
                var origin = protocol + sr_origin;
                // Allow absolute or scheme relative URLs to same origin
                return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                    (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                    // or any other URL that isn't scheme relative or absolute i.e relative.
                    !(/^(\/\/|http:|https:).*/.test(url));
            }
            
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }
    });
    
    Pusher.log = function(message) {
        console.log(message);
    };
    /* Creates an update channel for the auction */
    window.createUpdateChannel = function(auction_id, user_id) {
        // Move this key to a centralized file 
        var pusher = new Pusher('6f1c0b6c435fb05bea49', {
            encrypted: true,
            authEndpoint: '/pusher_auth'
        });
        var channel = pusher.subscribe('private-auction-' + auction_id);
        channel.bind('update', function(data) {
            if (data.bid) {
                var bidClass = '';
                if (data.bid.bidder_id == user_id) bidClass = 'mine';
                var bid = $(
                    '<div class="bid ' + bidClass + '" style="display:none">' +
                        '<span class="username">User ' +
                        data.bid.bidder_id +
                        '</span> bid $<span class="bid_amount">' +
                        (data.bid.amount / 100) +
                        '</span> at <span class="bid_date">' +
                        data.bid.time +
                        '</span>' + 
                        '</div>'
                );
                
                $('#bid_history').prepend(bid);
                bid.show('shake');
            } else if (data.ended) {
                
                if (data.winner_id == user_id) {
                    $('#ended').append($(
                        '<span class="won"> Congratulations!! You won this item!! </span>'
                    ));
                }
                $('#ended').show('shake');

                if (data.winner_id == user_id) {
                    $('#dialog').html('<p>Congratulations!! You won this item!!</p>');
                    $('#dialog').dialog();
                } else {
                    $('#dialog').html('<p>Sorry :( You did not win this item.</p>');
                    $('#dialog').dialog();
                }
            }
        });
    };

    $('#submit_bid').submit(function(event) {
        event.preventDefault();
        $.ajax({
            url: $('#submit_bid').attr('action'),
            type: "POST",
            data: $('#submit_bid').serialize(),
            dataType: "json",
            success: function(data) {
                if (data.error) {
                    $('#errDialog').html('<p>' + data.error + '</p>');
                    $('#errDialog').dialog();
                } else if (data.success) {
                    $('#dialog').html('<p>' + data.success + '</p>');
                    $('#dialog').dialog();
                } else {
                    alert(data);
                }
            },
            error: function(errMsg) {
                $('#errDialog').html('<p>' + errMsg + '</p>');
            }
        });
    });    
});
