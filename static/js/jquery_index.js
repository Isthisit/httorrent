
$(document).ready(function() {
	get_torrents();
})

function get_torrents() {
	$.getJSON('/httorrent/?torrent', function(data) {
		var items = [];

		$('tr').remove('#torrent_row');

		$.each(data.torrents, function(key, val) {
			items.push('<tr id="torrent_row">');
			items.push('<th>');
			items.push('<a href="' + val.hash + '">' + val.name + '</a>');
			items.push('</th>');
			items.push('<td>' + val.completed + '</td>');
			items.push('<td>' + val.size + '</td>');
			items.push('<td>' + val.down_rate + '</td>');
			items.push('<td>' + val.up_rate + '</td>');
			items.push('</tr>');
		})

		$('#torrents').append(items.join('\n'));
		$('#status').empty();
		$('#status').append('<p>Download Rate: ' + data.download_rate + ' KiB/s</p>');
		$('#status').append('<p>Upload Rate: ' + data.upload_rate + ' KiB/s</p>');

		setTimeout('get_torrents()', 5000);
	})
	.error(function () {
		$('tr').remove('#torrent_row');

		var items = []
		items.push('<tr id="torrent_row">');
		items.push('<th>Could not fetch torrents!</tr>');
		$('#torrents').append(items.join('\n'));

		setTimeout('get_torrents()', 60000);
	});
}

$(function() {
	var filename = $("#id_file")
	// Dialog
	$('#dialog').dialog({
		autoOpen: false,
		width: 600,
		buttons: {
			"Upload torrent": function() { 
				$('#file_form').submit();
				$(this).dialog("close"); 
			}, 
			"Cancel": function() { 
				$(this).dialog("close"); 
			} 
		},
		modal: true
	});
	
	// Dialog Link
	$('#dialog_link').button().click(function(){
		$('#dialog').dialog('open');
		return false;
	});

	//hover states on the static widgets
	$('#dialog_link, ul#icons li').hover(
		function() { $(this).addClass('ui-state-hover'); }, 
		function() { $(this).removeClass('ui-state-hover'); }
	);
});
