
	const transformPosts = () => {
		var stickynotes = document.querySelectorAll("#stickynote");

		[].forEach.call(stickynotes, function(note) {
			let max = 10
			let min = -10
			let range = max - min + 1;
			var angle = (Math.floor(Math.random() * range) + min);
			note.style.transform = "rotate(" + angle + "deg)";
			
			
			
			note.style.top = (angle*1.5) +"px";
		});
	};
	
	const setRandomImages = () => {
		var theImages = new Array()

		theImages[0] = 'cat.jpg'
		theImages[1] = 'hexR.svg'
		theImages[2] = 'logo.png'
		theImages[3] = 'yellow.svg'
		theImages[3] = 'star_magnet.svg'
		theImages[3] = 'cat.jpg'
		theImages[3] = 'yellow.svg'

		
		
		var postimages = document.querySelectorAll("#postimage");
		
		[].forEach.call(postimages, function(postimage) {
			var j = 0
			var p = theImages.length;
			var whichImage = Math.round(Math.random()*(p-1));
			
			postimage.src = "assets/"+theImages[whichImage];
			
		});
	}
	

	const setRandomImageTxts = () => {
		var txts = new Array()

		txts[0] = "How can I improve my art skills?"
		txts[1] = "I need help with my art project."
		txts[2] =  "I'm stuck on my art. "
		txts[3] = "I don't know what to do next with my art."
		txts[4] =  "I need some inspiration for my art."

		
		
		var stickynotedescs = document.querySelectorAll("#stickynotedesc");
		
		[].forEach.call(stickynotedescs, function(desc) {
			var j = 0
			var p = txts.length;
			var whichTxt = Math.round(Math.random()*(p-1));
			
			desc.innerHTML = txts[whichTxt];
			
		});
	}

	transformPosts();
	setRandomImages();
	setRandomImageTxts();
