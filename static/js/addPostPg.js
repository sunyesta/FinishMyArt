// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Thanks to https://stackoverflow.com/questions/10420352/converting-file-size-in-bytes-to-human-readable-string
/**
 * Format bytes as human-readable text.
 *
 * @param bytes Number of bytes.
 * @param si True to use metric (SI) units, aka powers of 1000. False to use
 *           binary (IEC), aka powers of 1024.
 * @param dp Number of decimal places to display.
 *
 * @return Formatted string.
 */
function humanFileSize(bytes, si=false, dp=1) {
  const thresh = si ? 1000 : 1024;

  if (Math.abs(bytes) < thresh) {
    return bytes + ' B';
  }

  const units = si
    ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
  let u = -1;
  const r = 10**dp;

  do {
    bytes /= thresh;
    ++u;
  } while (Math.round(Math.abs(bytes) * r) / r >= thresh && u < units.length - 1);


  return bytes.toFixed(dp) + ' ' + units[u];
}

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        files: [],
        posts: [],
        /*
        file_name: null, // File name
        file_type: null, // File type
        file_date: null, // Date when file uploaded
        file_path: null, // Path of file in GCS
        file_size: null, // Size of uploaded file
        download_url: null, // URL to download a file
        data_url, // secret baby that shows pics
        */
        add_description:"",
        add_title:"",
        loaded: false,
        uploading: false, // upload in progress
        deleting: false, // delete in progress
        delete_confirmation: false, // Show the delete confirmation thing.
        display_warning: false,
        test_val: "",
        current_post: "",
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };



    app.out = () => {
        app.vue.display_warning = false;

    }
    app.over = () => {
        app.vue.display_warning = true;
    }


    app.publish = function(parent_id){
        let img_id = app.vue.files[app.vue.files.length - 1].id;
        axios.post(add_post_inner_url, {title: app.vue.add_title, description: app.vue.add_description, image_id: img_id, parent_id: parent_id,});
    }
    //change so it is a call and resposne
    
    app.files_info = function (img_idx) {
        let img = app.vue.files[img_idx];
        if (img.file_path) {
            let info = "";
            if (img.file_size) {
                info = humanFileSize(img.file_size.toString(), si=true);
            }
            if (img.file_type) {
                if (info) {
                    info += " " + img.file_type;
                } else {
                    info = img.file_type;
                }
            }
            if (info) {
                info = " (" + info + ")";
            }
            if (img.file_date) {
                let d = new Sugar.Date(img.file_date + "+00:00");
                info += ", uploaded " + d.relative();
            }
            return img.file_name + info;
        } else {
            return "";
        }
    }
    

    //change so its like h5
    app.set_result = function (r) {

    }

    app.upload_file = function (event) {
        let input = event.target;
        let file = input.files[0];
        if (file) {
            app.vue.uploading = true;
            let file_type = file.type;
            let file_name = file.name;
            let file_size = file.size;
            // Requests the upload URL.
            axios.post(obtain_gcs_url, {
                action: "PUT",
                mimetype: file_type,
                file_name: file_name
            }).then ((r) => {
                let upload_url = r.data.signed_url;
                let file_path = r.data.file_path;
                // Uploads the file, using the low-level interface.
                let req = new XMLHttpRequest();
                // We listen to the load event = the file is uploaded, and we call upload_complete.
                // That function will notify the server `of the location of the image.
                req.addEventListener("load", function () {
                    app.upload_complete(file_name, file_type, file_size, file_path);
                });
                // TODO: if you like, add a listener for "error" to detect failure.
                req.open("PUT", upload_url, true);
                req.send(file);
            });
        }

    }

    app.delete_file = function (img_idx) {
        //change to get data from browser for which to delete and not to auto
        //set to the user's single image
        let img = app.vue.files[img_idx];
        if (!app.vue.delete_confirmation) {
            app.vue.delete_confirmation = true;
        } else {
            // It's confirmed.
            app.vue.delete_confirmation = false;
            app.vue.deleting = true;
            // Obtains the delete URL.
            let file_path = img.file_path;
            axios.post(obtain_gcs_url, {
                action: "DELETE",
                file_path: file_path,
            }).then(function (r) {
                let delete_url = r.data.signed_url;
                if (delete_url) {
                    // Performs the deletion request.
                    let req = new XMLHttpRequest();
                    req.addEventListener("load", function () {
                        app.deletion_complete(file_path);
                    });
                    // TODO: if you like, add a listener for "error" to detect failure.
                    req.open("DELETE", delete_url);
                    req.send();

                }
            });
        }
    };

    app.download_file_init = function () {
        for (let i = 0, len = app.vue.files.length; i < len; i++) {
            axios.post(obtain_gcs_url, {
                action: "GET",
                file_path: app.vue.files[i].file_path,
            }).then(function (r) {
                app.vue.files[i].data_url = r.data.signed_url;
            });
        }
    }

    app.upload_complete = function (file_name, file_type, file_size, file_path) {
        // We need to let the server know that the upload was complete;
        app.vue.loaded = true;
        axios.post(notify_url, {
            file_name: file_name,
            file_type: file_type,
            file_path: file_path,
            file_size: file_size,
        }).then(function (response) {
            app.vue.uploading = false;
            app.vue.files.push({
                file_name: file_name,
                file_type: file_type,
                file_path: file_path,
                file_size: file_size,
                file_date: response.file_date,
                download_url: response.download_url,
            });
            app.vue.file_info = app.files_info(app.vue.files.length-1);
        });
    }
    app.deletion_complete = function (file_path) {
        // We need to notify the server that the file has been deleted on GCS.
        axios.post(delete_url, {
            file_path: file_path,
        }).then (function (r) {
            app.vue.deleting =  false;
            // change to seek file in array and delete it
            for (let i = 0, len = app.vue.files.length; i < len; i++) {
                if(app.vue.files[i].file_path === file_path){
                    app.vue.files.splice(i, 1);
                    app.enumerate(app.vue.files);
                    break;
                }
            } 
        })
    }

    app.download_file = function (img_idx) {
        let img = app.vue.files[img_idx];
        if (img.download_url) {
            let req = new XMLHttpRequest();
            req.addEventListener("load", function () {
                app.do_download(req);
            });
            req.responseType = 'blob';
            req.open("GET", img.download_url, true);
            req.send();
        }
    };

    app.do_download = function (req) {
        // This Machiavellic implementation is thanks to Massimo DiPierro.
        // This creates a data URL out of the file we downloaded.
        let data_url = URL.createObjectURL(req.response);
        // Let us now build an a tag, not attached to anything,
        // that looks like this:
        // <a href="my data url" download="myfile.jpg"></a>
        let a = document.createElement('a');
        a.href = data_url;
        a.download = app.vue.file_name;
        // and let's click on it, to do the download!
        a.click();
        // we clean up our act.
        a.remove();
        URL.revokeObjectURL(data_url);
    };


    app.set_current_post = function (post_id){
        let posts = app.data.posts;
        for (let i = 0; i < posts.length; i++){
            let post = posts[i];
            if(post.id == post_id){
                app.data.current_post = post
                break;
            }
        }
    }
    
    app.get_artwork_url = function(post_id){
        return "[[=URL('artwork',"+post.id+")]]";
    }

    app.get_posts_of_parentPost = function(parent_id){
        let posts = app.data.posts;
        let filtered_posts = [];
        for (let i = 0; i < posts.length; i++){
            let post = posts[i];
            if(post.parent_post == parent_id){
                filtered_posts.push(post)
            }
        }
        return filtered_posts;
    }

    app.computed = {
    };

    

    // This contains all the methods.
    app.methods = {
        publish: app.publish,
        upload_file: app.upload_file, // Uploads a selected file
        delete_file: app.delete_file, // Delete the file.
        download_file: app.download_file, // Downloads it.
        out: app.out,
        over: app.over,
        set_current_post: app.set_current_post,
        get_artwork_url: app.get_artwork_url,
        get_posts_of_parentPost: app.get_posts_of_parentPost,
    };
    
    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        computed: app.computed,
        methods: app.methods,
    });

    //maybe change this so it can intialize all post photos??
    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(files_info_url).then(function (response) {
            let fil = response.data.rows;
            app.enumerate(fil);
            app.vue.files = fil;
            app.download_file_init();
            axios.get(get_posts_url).then(function (response2) {
                let posts = response2.data.posts;
                app.enumerate(posts);
                app.vue.posts = posts;

                let files = app.vue.files;
                for (let p = 0; p < posts.length; p++) {
                    let post = posts[p];
                    
                    for (let f = 0; f < files.length; f++){
                        let file = files[f];
                        if(post.image_id == file.id){
                            post.file = file
                            break;
                        }
                    }

                }
            });
        });
    };



    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);