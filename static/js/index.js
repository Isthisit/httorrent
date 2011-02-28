var httorrent_ajax = {
	init: function() {
		// Grab the elements we'll need
		httorrent_ajax.torrents_table = document.getElementById('torrents');
		httorrent_ajax.get_torrents();
	},
	get_torrents: function() {
		var cObj = YAHOO.util.Connect.asyncRequest('GET', '/httorrent/?torrent', httorrent_ajax.torrent_callback);
		setTimeout(function() { httorrent_ajax.get_torrents(); }, 5000 );
	},
	clear_table: function() {
		var rows = httorrent_ajax.torrents_table.getElementsByTagName('tr');

		for(var i=0; i < rows.length; i++) {
			if((rows[i].id != 'torrent_header')) {
				httorrent_ajax.torrents_table.removeChild(rows[i]);
				// adjust index so it points at the right thing after we deleted the current 'tr'
				i--;
			}
		}
	},
	torrent_callback: {
		success: function(o) {
			var response_obj = eval('(' + o.responseText + ')');

			httorrent_ajax.clear_table();
			for(var torrent in response_obj) {
				// Create a row for this torrent.
				var row = document.createElement('tr');
				var row_name = document.createElement('th');
				row_name.innerHTML = response_obj[torrent].name;
				var row_complete = document.createElement('td');
				row_complete.innerHTML = response_obj[torrent].completed;
				var row_size = document.createElement('td');
				row_size.innerHTML = response_obj[torrent].size;
				var row_down_rate = document.createElement('td');
				row_down_rate.innerHTML = response_obj[torrent].down_rate;
				var row_up_rate = document.createElement('td');
				row_up_rate.innerHTML = response_obj[torrent].up_rate;
				// Add all rows to the torrent table
				row.appendChild(row_name);
				row.appendChild(row_complete);
				row.appendChild(row_size);
				row.appendChild(row_down_rate);
				row.appendChild(row_up_rate);

				// Update table
				httorrent_ajax.torrents_table.appendChild(row);
			}
		},
		failure: function(o) {
			alert('An error has occurred');
		}
	}
};

YAHOO.util.Event.addListener(window, 'load', httorrent_ajax.init);
