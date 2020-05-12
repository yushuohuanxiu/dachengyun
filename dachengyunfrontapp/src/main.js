import Vue from 'vue'
import App from './App.vue'
import axios from "axios";
import vueAxios from 'vue-axios';
import {BootstrapVue, IconsPlugin} from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use(vueAxios, axios);

Vue.config.productionTip = false
axios.defaults.headers.post['Content-Type'] = 'application/json;charset=UTF-8';

new Vue({
    render: h => h(App),
}).$mount('#app')
