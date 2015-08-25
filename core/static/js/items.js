Pusher.log = function(message) {
    console.log(message);
};
window.createUpdateChannel = function(auction_id) {
    var pusher = new Pusher('6f1c0b6c435fb05bea49', {
        encrypted: true,
        authEndpoint: '/pusher_auth'
    });
    var channel = pusher.subscribe('private-auction-' + auction_id);
    channel.bind('update', function(data) {
        $('#selling-' + auction_id).html(data.bid.amount / 100);
    });
};
