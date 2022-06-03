
// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        loaded: false,
        rows:[],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
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
        
        axios.get(load_posts_url).then(function(response) {
            app.vue.rows = app.enumerate(response.data.rows);
            for (let i = 0; i < app.vue.rows.length; i++) {
                app.vue.rows[i].loaded = true;
                axios.get(get_image_url, {params: {row_id: app.vue.rows[i].id}}).then(function(response) {
                    Vue.set(app.vue.rows[i], "image", 'art/' + response.data.image.image);

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
