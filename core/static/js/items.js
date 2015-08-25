Pusher.log = function(message) {
    console.log(message);
};
window.createUpdateChannel = function(key, auction_id) {
    var pusher = new Pusher(key, {
        encrypted: true,
        authEndpoint: '/pusher_auth'
    });
    var channel = pusher.subscribe('private-auction-' + auction_id);
    channel.bind('update', function(data) {
        $('#selling-' + auction_id).html(data.bid.amount / 100);
    });
};
