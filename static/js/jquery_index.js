
$(document).ready(function() {
	get_torrents();
})

function get_torrents() {
	$.getJSON('/httorrent/?torrent', function(data) {
		var items = [];

		$('tr').remove('#single_torrent');

		$.each(data, function(key, val) {
			items.push('<tr id="single_torrent">');
			items.push('<th>' + val.name + '</th>');
			items.push('<td>' + val.completed + '</td>');
			items.push('<td>' + val.size + '</td>');
			items.push('<td>' + val.down_rate + '</td>');
			items.push('<td>' + val.up_rate + '</td>');
			items.push('</tr>');
		})

		$("#torrents").append(items.join('\n'));
		setTimeout('get_torrents()', 5000);
	})
}

