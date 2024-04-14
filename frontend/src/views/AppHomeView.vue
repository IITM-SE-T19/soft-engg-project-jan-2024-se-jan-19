<template>
  <div class="home-div">
    <div class="home-menu">
      <b-button
        variant="link"
        :to="{ path: '/login' }"
        class="home-button">
        <img src="../assets/btn_login.png" alt="Link to Login to OSTS" height="20%" style="height:22vh">
      </b-button>

      <b-button
        variant="link"
        :to="{ path: '/register' }"
        class="home-button">
        <img src="../assets/btn_register.png" alt="Link to register new OSTS user" style="height:22vh">
      </b-button>

      <b-button
        variant="link"
        href="https://bit.ly/ostsv2"
        target="_blank"
        class="home-button">
        <img src="../assets/btn_about.png" alt="About OSTS" height="20%" style="height:22vh">
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

.home-menu {
  position: fixed;
  top: 5%;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end; /* Aligns the menu to the right */
  padding: 20px;
}

</style>
