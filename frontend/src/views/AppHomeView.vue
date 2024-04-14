<template>
  <div class="home-div">
    <div class="vertical-menu">
      <b-button
        variant="link"
        :to="{ path: '/login' }"
        class="home-button">
        <img src="../assets/btn_login.png" alt="Button 1">
      </b-button>

      <b-button
        variant="link"
        :to="{ path: '/register' }"
        class="home-button">
        <img src="../assets/btn_register.png" alt="Button 1">
      </b-button>

      <b-button
        variant="link"
        href="https://bit.ly/ostsv2"
        target="_blank"
        class="home-button">
        <img src="../assets/btn_about.png" alt="Button 1">
      </b-button>


      </div>
    </div>
</template>

<script>
import * as common from "../assets/common.js";

export default {
  name: "AppHomeView",
  components: {},
  data() {
    return {
      show: true,
    };
  },
  methods: {},
};
</script>

<style>
.home-div {
  background-image: url("../assets/home_page_image.jpg");
  height: 100vh;
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
}

.vertical-menu {
  position: fixed;
  top: 5%;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end; /* Aligns the menu to the right */
  padding: 20px;
}

.vertical-menu-button {
  margin-bottom: 10px;
}
</style>
