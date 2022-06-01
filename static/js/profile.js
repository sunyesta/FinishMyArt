
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
                let images = result.data.images.image_url;
                let description = result.data.images.description;
                app.enumerate(images);
                app.vue.images = images;
                app.vue.description = description;
            });
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
