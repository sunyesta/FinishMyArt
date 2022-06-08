
// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        current_tab: "",
        in_progress_images: [],
        finished_images: [],
        helped_images: [],
        images: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.set_tab = function (tab_name) {
        app.vue.current_tab = tab_name
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        set_tab: app.set_tab,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods,
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        //axios.get(load_posts_url).then(function(response) {
        //});
        app.vue.current_tab = "in_progress";
        axios.get(get_images_url)
        .then((result) => {
            // We set them
            let in_progress_images = result.data.in_progress_images;
            let finished_images = result.data.finished_images;
            let images = result.data.images;

            app.enumerate(images);
            app.vue.in_progress_images = app.enumerate(in_progress_images);
            app.vue.finished_images = app.enumerate(finished_images);

            //in progress images set images
            for (let i = 0; i < app.vue.in_progress_images.length; i++) {
                axios.get(get_image_url, {params: {row_id: app.vue.in_progress_images[i].id}}).then(function(response) {
                    Vue.set(app.vue.in_progress_images[i], "image", 'art/' + response.data.image.file_name);
                });
            }

            //finished images set images
            for (let i = 0; i < app.vue.finished_images.length; i++) {
                axios.get(get_image_url, {params: {row_id: app.vue.finished_images[i].id}}).then(function(response) {
                    Vue.set(app.vue.finished_images[i], "image", 'art/' + response.data.image.file_name);
                });
            }
        });
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
