var ajax_example = {
	init: function() {
		// Grab the elements we'll need
		ajax_example.torrents_table = document.getElementById('torrents');
		ajax_example.get_torrents();
	},
	get_torrents: function() {
		var cObj = YAHOO.util.Connect.asyncRequest('GET', '/httorrent/?torrent', ajax_example.torrent_callback);
		setTimeout(function() { ajax_example.get_torrents(); }, 5000 );
	},
	clear_table: function() {
		var rows = ajax_example.torrents_table.getElementsByTagName('tr');

		for(var i=0; i < rows.length; i++) {
			if((rows[i].id != 'torrent_header')) {
				ajax_example.torrents_table.removeChild(rows[i]);
				// adjust index so it points at the right thing after we deleted the current 'tr'
				i--;
			}
		}
	},
	torrent_callback: {
		success: function(o) {
			var response_obj = eval('(' + o.responseText + ')');

			ajax_example.clear_table();
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
				ajax_example.torrents_table.appendChild(row);
			}
		},
		failure: function(o) {
			alert('An error has occurred');
		}
	}
};

YAHOO.util.Event.addListener(window, 'load', ajax_example.init);
