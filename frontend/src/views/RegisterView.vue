<!-- TEAM 19 - PB Updated UI for OSTS V2 and Team 19  -->
<!-- TEAM 19 - JA Updated User Registration Form to include Discourse Username -->

<!-- Registration Page: Register New User -->

<template>
  <div>
    <div class="login-div">
    <h1 style="text-align: left">Register</h1>
    </div>
  <div class="register-form">
    <div style="margin: 3%; padding: 3%; width: 50%">
      <h3 style="text-align: left">Register</h3>
      <br />
      <b-form @submit="onSubmit" @reset="onReset" v-if="show">
        <b-form-group
          ><b-form-input
            id="input-first-name-register"
            v-model="form.first_name"
            type="text"
            placeholder="Enter first name"
            :state="discourseUserExists"
            aria-describedby="input-live-feedback-first-name"
            required
          ></b-form-input>
          <b-form-invalid-feedback id="input-live-feedback-first-name">
            Enter at least 3 letters of first name
          </b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
          ><b-form-input
            id="input-last-name-register"
            v-model="form.last_name"
            type="text"
            placeholder="Enter last name (Optional)"
          ></b-form-input
        ></b-form-group>

        <b-form-group label="Select role:" v-slot="{ ariaDescribedby }">
          <b-form-radio-group
            id="radio-group-role-register"
            v-model="form.role"
            :options="role_options"
            :aria-describedby="ariaDescribedby"
            name="radio-group-role"
          ></b-form-radio-group>
        </b-form-group>

        <b-form-group
          ><b-form-input
            id="input-email-register"
            v-model="form.email"
            type="email"
            placeholder="Enter email"
            required
            
          ></b-form-input>
          <span v-if="userExists">
              User with email {{ form.email }} exists with username {{ discourseUsername }}
            </span>
        
        </b-form-group>
        <b-form-group>
<!-- #TEAM19-AJ -->
        <p
          ><b-form-input
            id="input-discourse-username"
            v-model="form.discourse_username"
            type="text"
            placeholder="Enter Discourse Username"
            :state="discourseUserExists"
            aria-describedby="input-live-feedback-discourse-username"
            required
            @blur="checkUserExists"
            @focus="focusON=true;"
          ></b-form-input>
          <span v-if="loading">Validating Discourse username <b-spinner small ></b-spinner></span></p>
          <div v-if="form.discourse_username.length >= 3">
            <span v-if="this.discourseUserExists && this.loading===false && this.focusON===false" style="color: green;">&#10004; Discourse username is valid.</span>
            <span v-if="!this.discourseUserExists && this.loading===false && this.focusON===false" style="color: red;">&#10008; Discourse username not found.</span>
          </div>
     
    </b-form-group>

        <b-form-group
          ><b-form-input
            id="input-password-register"
            v-model="form.password"
            placeholder="Enter password"
            type="password"
            :state="check_password"
            aria-describedby="input-live-feedback-password"
            required
          ></b-form-input>
          <b-form-invalid-feedback id="input-live-feedback-password">
            Password should contain letters A-Z a-z and numbers 0-9 only and should be atleast 4 and
            atmost 8 characters long.
          </b-form-invalid-feedback>
        </b-form-group>

        <b-form-group
          ><b-form-input
            id="input-retype-password-register"
            v-model="form.retype_password"
            placeholder="Retype password"
            type="password"
            :state="check_retype_password"
            aria-describedby="input-live-feedback-retype-password"
            required
          ></b-form-input>
          <b-form-invalid-feedback id="input-live-feedback-retype-password">
            Password did not match.
          </b-form-invalid-feedback>
        </b-form-group>
        <br />
        <!-- #Team19-AJ -->
        <b-button style="margin: 10px" type="submit" variant="primary" :disabled="!discourseUserExists">Submit</b-button>

        <b-button style="margin: 10px" type="reset" variant="danger">Reset</b-button>
      </b-form>
      <br />
      <p>Already registered? Please <b-link href="/login">Login here</b-link></p>
      <p>Go to <b-link href="/home">Home Page</b-link></p>
    </div>
  </div>
</div>
</template>

<script>
import * as common from "../assets/common.js";

export default {
  name: "RegisterView",
  components: {},
  data() {
    return {
      role_options: [
        { text: "Student", value: "student" },
        { text: "Support", value: "support" },
        { text: "Admin", value: "admin" },
      ],
      form: {
        first_name: "",
        last_name: "",
        role: "student",
        email: "",
        password: "",
        retype_password: "",

        // #TEAM19-AJ
        discourse_username: "",  

      },

    // #TEAM19-AJ
      userExists: false,
      discourseUserExists: false,
      // #TEAM19-SV
      loading:false, focusON:true,

      show: true,
    };
  },
  methods: {
    onSubmit(event) {
      event.preventDefault();
      alert('You are creating a new account. Click "Ok" to proceed?');
      this.$log.info("Submitting Registration form");

      this.form.password = btoa(this.form.password);
      this.form.retype_password = btoa(this.form.retype_password);

      fetch(common.AUTH_API_REGISTER, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(this.form),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.category == "success") {
            this.flashMessage.success({
              message: data.message,
            });
            this.$router.push("/login");
          }
          if (data.category == "error") {
            this.flashMessage.error({
              message: data.message,
            });
          }
        })
        .catch((error) => {
          this.$log.error(`Error : ${error}`);
          this.flashMessage.error({
            message: "Internal Server Error",
          });
        });
    },
    onReset(event) {
      event.preventDefault();
      this.form.first_name = "";
      this.form.last_name = "";
      this.form.email = "";
      this.form.password = "";
      this.form.retype_password = "";

      // #TEAM19-AJ
      this.form.discourse_username= "",
      // Trick to reset/clear native browser form validation state
      this.show = false;
      this.$nextTick(() => {
        this.show = true;
      });
    },

    checkUserExists() {
      if(this.form.discourse_username.length<3) return; // Team 19 SV

      this.loading=true; // Team 19 SV
      this.focusON=false; // Team 19 SV

     fetch(`http://localhost:5000/api/v1/discourse/user/${this.form.discourse_username}`, {
      method: "GET", 
     })
     .then((response) => {
      this.loading=false;
      if (response.status === 200) {
       this.discourseUserExists = true;
      } else if (response.status === 404) {
    // User does not exist (status 404)
       this.discourseUserExists = false;
      } else {
    // Handle other error cases
        console.error("Error checking user existence. Status code:", response.status);
      }
    })
    .catch((error) => {
      console.error("Error checking user existence:", error);
    });
  },

},
  computed: {
    check_name() {
      return this.form.first_name.length > 2 ? true : false;
    },
    check_password() {
      let password = this.form.password;
      if (password.length < 4 || password.length > 9) {
        return false;
      }
      const valid_char_array = Array.from(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
      );
      const password_array = Array.from(password);
      for (let i = 0; i < password_array.length; i++) {
        if (!valid_char_array.includes(password_array[i])) {
          return false;
        }
      }
      return true;
    },
    check_retype_password() {
      return this.form.password === this.form.retype_password && this.check_password ? true : false;
    },
  },
  
};
</script>

<style>
.login-div {
  background-image: url("../assets/osts_logo.png");
  background-color: #D2FFC6;
  height: 9vh;
  background-position: right;
  background-repeat: no-repeat;
  background-size: auto;
  margin-right:8px;
  margin-top:8px;
  padding-left:8px;
  padding-top:18px;
  vertical-align: middle;
}
</style>
