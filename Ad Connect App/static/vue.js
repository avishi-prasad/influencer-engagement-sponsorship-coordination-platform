console.log('Checking if Vue.js is loaded...');
Vue.component('user-login', {
    template:` 
        <div>
            <h2>User Login</h2>
            <form @submit.prevent="validateForm" id="myForm">
                <p>
                    <b>Login As: </b>
                    <input type="radio" name="role" value="sponsor" v-model="role">Sponsor
                    <input type="radio" name="role" value="influencer" v-model="role" required>Influencer
                </p>
                <p>
                    Username: <input type="text" v-model="user_name" placeholder="Enter Username" required>
                </p>
                <p>
                    Password: <input type="password" v-model="user_pass" placeholder="Enter Password" required>
                </p>
                <button type="button" @click="validateForm" style="background-color: #FFD700;">Login</button>
                <button type="button" @click="validateRegister" style="background-color: #FFD700;">Register</button>
            </form>
            <p v-if="message" style="color: red;">{{ message }}</p>
        </div>`
    ,
    data: function() {
        return {
            role: "",
            user_name: "",
            user_pass: "",
            message: ""
        };
    },
    methods: {
        validateForm(event) {
            if (!this.role || !this.user_name || !this.user_pass) {
                this.message = "Please fill out all required fields.";
            } else {
                this.message = "";
                this.handleLogin();
            }
        },
        validateRegister(event) {
            if (!this.role || !this.user_name || !this.user_pass) {
                this.message = "Please fill out all required fields.";
            } else {
                this.message = "";
                this.handleRegister();
            }
        },
        handleLogin() {
            axios.post('/login', {
                role: this.role,
                username: this.user_name,
                password: this.user_pass
            })
            .then(response => {
                if (response.data.success) {
                    window.location.href = `/${this.role}/${this.user_name}/profile`;
                } else {
                    this.message = response.data.message;
                }
            })
            .catch(error => {
                this.message = 'An error occurred during login.';
            });
        },
        handleRegister() {
            axios.post('/register', {
                role: this.role,
                username: this.user_name,
                password: this.user_pass
            })
            .then(response => {
                if (response.data.success) {
                    this.message = 'Registration successful. Please login.';
                    this.resetForm();
                } else {
                    this.message = response.data.message;
                }
            })
            .catch(error => {
                this.message = 'An error occurred during registration.';
            });
        },
        resetForm() {
            this.role = "";
            this.user_name = "";
            this.user_pass = "";
        }
    }
});
Vue.component('admin-login',{
    template:`<div>
    <h2>Admin Login</h2>
    <form @submit.prevent="admin_login">
    <p>Admin Id: <input type="text" v-model="admin_id" placeholder="Enter Admin Id" required></p>
    <p>Password: <input type="password" v-model="admin_pass" placeholder="Enter Password" required></p>
    <button @click="validateForm" style="background-color: #FFD700;">Login</button>
    </form>
    <p v-if="message.length" v-for="msg in message" style="color: red;">{{ msg }}</p>
    </div>`,
    data:function(){
        return{
        admin_id:"",
        admin_pass:"",
        message: []
        }
    },
    methods:{
        validateForm(event) {
            if (!this.admin_id || !this.admin_pass) {
                this.message.push("Please fill out all required fields");
                event.preventDefault(); 
            } else {
                this.message = [];
                this.admin_login();
            }
        },
        admin_login() {
            this.message = [];
            const correct_admin_id = "app_admin_00";
            const correct_admin_pass = "@1029";
                    
            if (this.admin_id !== correct_admin_id) {
                this.message.push("Incorrect Admin Id");
            }
            else if (this.admin_pass !== correct_admin_pass) {
                this.message.push("Incorrect Password");
            }
            if(this.admin_id === correct_admin_id && this.admin_pass === correct_admin_pass){
                window.location.href = "/admin_dashboard";
            }
        }
    }
});
Vue.component('ad-camp', {
    template: `
      <div class="modal">
        <div class="modal-content">
          <span class="close" @click="closeModal">&times;</span>
          <h5>Add New Campaign : </h5>
          <form @submit.prevent="submitCampaign">
            <div>
              <label for="name">Campaign Name:</label>
              <input type="text" v-model="name" required>
            </div><br>
            <div>
              <label for="description">Description:</label>
              <textarea v-model="description" required></textarea>
            </div><br>
            <div>
              <label for="budget">Budget (in Rupees):</label>
              <input type="text" v-model="budget" placeholder="Define bugdet range" required>
            </div><br>
            <div>
              <label for="end_date">End Date:</label>
              <input type="date" v-model="end_date" required>
            </div><br>
            <p v-if="message">{{message}}</p>
            <button style="background-color: #FFD700;" type="submit">Submit</button>
          </form>
        </div>
      </div>
    `,
    props: ['username'],
    data() {
      return {
        name: '',
        description: '',
        budget: '',
        end_date:'',
        message: '',
      };
    },
      methods: {
        closeModal() {
          console.log("Closing modal");
          this.$emit('close');
        },
        submitCampaign() {
          console.log("Submitting campaign");
          const campaign = {
            name: this.name,
            description: this.description,
            budget: this.budget,
            end_date:this.end_date
          };
          this.$emit('submit', campaign);
          this.closeModal();
          window.location.href=`/sponsor/${this.username}/add_campaign`;
        }
      }
});

Vue.component('edit-camp', {
  template: `
    <div class="modal">
      <div class="modal-content">
        <span class="close" @click="closeModal">&times;</span>
        <h5>Edit Campaign : </h5>
        <form @submit.prevent="edit_submitCampaign">
          <div>
            <label for="name">Campaign Name:</label>
            <input type="text" v-model="name" required>
          </div><br>
          <div>
            <label for="description">Description:</label>
            <textarea v-model="description" required></textarea>
          </div><br>
          <div>
            <label for="budget">Budget (in Rupees):</label>
            <input type="text" v-model="budget" placeholder="Define bugdet range" required>
          </div><br>
          <div>
            <label for="end_date">End Date:</label>
            <input type="date" v-model="end_date" required>
          </div><br>
          <p v-if="message">{{message}}</p>
          <button style="background-color: #FFD700;" type="submit">Submit</button>
        </form>
      </div>
    </div>
  `,
  props: ['username','camp_name','camp_id','camp_desc','camp_budget','camp_end_date'],
  data() {
    return {
      id: this.camp_id,
      name: this.camp_name,
      description: this.camp_desc,
      budget: this.camp_budget,
      end_date:this.camp_end_date,
      message: '',
    };
  },
    methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      edit_submitCampaign() {
        console.log("Submitting campaign");
        const campaign = {
          id:this.id,
          name: this.name,
          description: this.description,
          budget: this.budget,
          end_date:this.end_date
        };
        this.$emit('submit', campaign);
        this.closeModal();
        window.location.href=`/sponsor/${this.username}/add_campaign`;
      }
    }
});

Vue.component('search-bar', {
  props: ['username'],
  data: function() {
      return {
          searchQuery: '',
          category: '',
          minBudget: '',
          maxBudget: ''
      };
  },
  template: `
      <div class="container mt-4">
          <div class="input-group mb-2">
            <input type="text" class="form-control" v-model="searchQuery" placeholder="Search by name or sponsor">
          </div>
          <div class="input-group mb-2">
            <input type="text" class="form-control" v-model="category" placeholder="Search by category">
          </div>
          <div class="input-group mb-2">
            <input type="number" class="form-control" v-model="minBudget" placeholder="Min Budget">
            <input type="number" class="form-control" v-model="maxBudget" placeholder="Max Budget">
          </div>
          <div class="input-group-append">
            <button class="btn btn-primary" type="button" @click="search">Search</button>
          </div>
      </div>
  `,
  methods: {
    search(event) {
        event.preventDefault();
        const url = `/influencer/${this.username}/search`;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: this.searchQuery,
                category: this.category,
                min_budget: this.minBudget,
                max_budget: this.maxBudget
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const campaignIds = data.campaigns
                window.location.href = `/influencer/${this.username}/search_results?campaign_ids=${campaignIds}`;
            } 
            else {
                
                window.location.href = `/influencer/${this.username}/search_results?campaign_ids=[]`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

});


Vue.component('sp-search-bar', {
    props: ['username'],
    data: function() {
      return {
        searchQuery: '',
        category: '',
        minFollowers: '',
        minRating: ''
    };
    },
    template: `
        <div class="container mt-4">
          <div class="input-group mb-2">
            <input type="text" class="form-control" v-model="searchQuery" placeholder="Search by name">
          </div>
          <div class="input-group mb-2">
            <input type="text" class="form-control" v-model="category" placeholder="Search by category">
          </div>
          <div class="input-group mb-2">
            <input type="number" class="form-control" v-model="minFollowers" placeholder="Min Followers">
            <input type="number" class="form-control" v-model="minRating" placeholder="Min Rating">
          </div>
          <div class="input-group-append">
            <button class="btn btn-primary" type="button" @click="search">Search</button>
          </div>
      </div>
    `,
    methods: {
      search(event) {
          event.preventDefault();  
          console.log("Search started");  
  
          const url = `/sponsor/${this.username}/search`;
          fetch(url, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                searchQuery: this.searchQuery,
                category: this.category,
                minFollowers: this.minFollowers,
                minRating: this.minRating
              })
          })
          .then(response => response.json())
          .then(data => {
              console.log("Search response:", data);  
              if (data.success) {
                  const influencerIds = data.influencers;  
                  window.location.href = `/sponsor/${this.username}/search_results?influencer_ids=${influencerIds}`;
              } else {
                
                  window.location.href = `/sponsor/${this.username}/search_results?influencer_ids=[]`;
              }
          })
          .catch(error => {
              console.error('Error:', error);
          });
      }
  }
    });
Vue.component('edit-desc', {
    template: `
      <div class="modal">
        <div class="modal-content">
           <span class="close" @click="closeModal">&times;</span>
           <h5>Edit Description : </h5>
           <form @submit.prevent="submitDesc">
            <div>
              <label for="desc">New Description:</label>
              <input type="textarea" v-model="desc" required>
            </div>
            <button style="background-color: #FFD700;" type="submit">Save</button>
          </form>
        </div>
      </div>
    `,
    props: ['username','description'],
    data() {
      return {
        desc: this.description,
      };
    },
    methods: {
        closeModal() {
          console.log("Closing modal");
          this.$emit('close');
        },
        submitDesc() {
            console.log("Submitting Desc");
            const description = {
                description: this.desc, 
            };
            this.$emit('submit', description);
            this.closeModal();
            window.location.href=`/influencer/${this.username}/profile`;
        }
      }
});

Vue.component('add-foll', {
  template: `
    <div class="modal">
      <div class="modal-content">
         <span class="close" @click="closeModal">&times;</span>
         <h5>Add/Edit no. of followers : </h5>
         <form @submit.prevent="submitFoll">
          <div>
            <label for="foll">No. of followers:</label>
            <input type="number" v-model="foll"  :placeholder="followers" required>
          </div>
          <button style="background-color: #FFD700;" type="submit">Save</button>
        </form>
      </div>
    </div>
  `,
  props: ['username','followers'],
  data() {
    return {
      foll: this.followers,
    };
  },
  methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      submitFoll() {
          console.log("Submitting Followers");
          const followers = {
              followers: this.foll, 
          };
          this.$emit('submit', followers);
          this.closeModal();
          window.location.href=`/influencer/${this.username}/profile`;
      }
    }
});

Vue.component('add-cat', {
  template: `
    <div class="modal">
      <div class="modal-content">
         <span class="close" @click="closeModal">&times;</span>
         <h5>Add/Edit category : </h5>
         <form @submit.prevent="submitCategory">
          <div>
            <label for="category">Category:</label>
            <input type="text" v-model="category" required>
          </div>
          <button style="background-color: #FFD700;" type="submit">Save</button>
        </form>
      </div>
    </div>
  `,
  props: ['username','category'],
  data() {
    return {
      category:this.category,
    };
  },
  methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      submitCategory() {
          console.log("Submitting Category");
          const category = {
              category: this.category, 
          };
          this.$emit('submit', category);
          this.closeModal();
          window.location.href=`/influencer/${this.username}/profile`;
      }
    }
});

Vue.component('add-email', {
  template: `
    <div class="modal">
      <div class="modal-content">
         <span class="close" @click="closeModal">&times;</span>
         <h5>Add/Edit email id : </h5>
         <form @submit.prevent="submitEmail">
          <div>
            <label for="email">Email Id:</label>
            <input type="text" v-model="email" required>
          </div>
          <button style="background-color: #FFD700;" type="submit">Save</button>
        </form>
      </div>
    </div>
  `,
  props: ['username','email'],
  data() {
    return {
      email:this.email,
    };
  },
  methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      submitEmail() {
          console.log("Submitting Email");
          const email = {
              email: this.email, 
          };
          this.$emit('submit', email);
          this.closeModal();
          window.location.href=`/influencer/${this.username}/profile`;
      }
    }
});

Vue.component('add-sp-email', {
  template: `
    <div class="modal">
      <div class="modal-content">
         <span class="close" @click="closeModal">&times;</span>
         <h5>Add/Edit Email id : </h5>
         <form @submit.prevent="submitEmail">
          <div>
            <label for="email">Email Id:</label>
            <input type="text" v-model="email" required>
          </div>
          <button style="background-color: #FFD700;" type="submit">Save</button>
        </form>
      </div>
    </div>
  `,
  props: ['username','email'],
  data() {
    return {
      email:this.email,
    };
  },
  methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      submitEmail() {
          console.log("Submitting Email");
          const email = {
            email: this.email, 
          };
          this.$emit('submit', email);
          this.closeModal();
          window.location.href=`/sponsor/${this.username}/profile`;
      }
    }
});

Vue.component('add-sp-cat', {
  template: `
    <div class="modal">
      <div class="modal-content">
         <span class="close" @click="closeModal">&times;</span>
         <h5>Add/Edit category : </h5>
         <form @submit.prevent="submitCategory">
          <div>
            <label for="category">Category:</label>
            <input type="text" v-model="category" required>
          </div>
          <button style="background-color: #FFD700;" type="submit">Save</button>
        </form>
      </div>
    </div>
  `,
  props: ['username','category'],
  data() {
    return {
      category:this.category,
    };
  },
  methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      submitCategory() {
          console.log("Submitting Category");
          const category = {
              category: this.category, 
          };
          this.$emit('submit', category);
          this.closeModal();
          window.location.href=`/sponsor/${this.username}/profile`;
      }
    }
});

Vue.component('send-req', {
  template: `
    <div class="modal" style="text-align: left;">
  <div class="modal-content">
    <span class="close" @click="closeModal">&times;</span>
    <h5>Send Request to {{ influencer_name }}:</h5>
    <div>
      <form v-if="campaigns.length" @submit.prevent="submitRequest">
        <label for="name"><b>Choose Campaign:</b></label>
        <div v-for="campaign in campaigns" :key="campaign.id">
          <input type="radio" :value="campaign.id" v-model="campaign_id"> {{ campaign.name }}
        </div>
        <br>
        <button style="background-color: #FFD700;" type="submit">Send</button>
      </form>
      <p v-else>Oops! No campaigns to send.</p>
    </div>
  </div>
</div>
`,
  props: ['username','influencer_id','influencer_name','campaigns'],
  data() {
    return {
      campaign_id: '',
      inf_id: this.influencer_id,
      influencer_name:this.influencer_name
    };
  },
    methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      submitRequest() {
        console.log("Sending Request");
        const request = {
          sp_name: this.username,
          campaign_id: this.campaign_id,
          inf_id: this.inf_id ,
          
        };
        this.$emit('submit', request);
        this.closeModal();
        window.location.href=`/sponsor/${this.username}/details/inf/${this.influencer_id}`;
      }
    }
});

Vue.component('send-req-inf', {
  template: `
    <div class="modal" style="text-align: left;" >
      <div class="modal-content">
        <span class="close" @click="closeModal">&times;</span>
        <h5>Sending Request for {{campaign_name}}: </h5>
        <form @submit.prevent="submitRequest">
          <p>Are you sure you want to send request for {{campaign_name}} ?</p>
          <button style="background-color: #FFD700;" type="submit">Confirm</button> <button  @click="closeModal">Close</button >
        </form>
      </div>
    </div>
  `,
  props: ['username','influencer_id','influencer_name','campaign_id','campaign_name'],
  data() {
    return {
      
      inf_id: this.influencer_id
      
    };
  },
    methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      submitRequest() {
        console.log("Sending Request");
        const req = {
          sp_name: this.username,
          campaign_id: this.campaign_id,
          inf_id: this.inf_id ,
          inf_name:this.influencer_name,
          requirements: this.requirements,
          amount: this.amount,
          
        };
        this.$emit('submit', req);
        this.closeModal();
        window.location.href=`/influencer/${this.username}/details/camp/${this.campaign_id}`;
      }
    }
});

Vue.component('rate', {
  template: `
    <div class="modal" style="text-align: left;" >
      <div class="modal-content">
        <span class="close" @click="closeModal">&times;</span>
        <h5>Rate {{influencer_name}}: </h5>
        <form @submit.prevent="submitRating">
          <div>
            <label for="rating"><b>Rating:</b></label>
            <div class="rating">
            <input type="radio" id="star5" name="rating" value="5" v-model="rating" required>
            <label for="star5" title="5 stars">★</label>
            <input type="radio" id="star4" name="rating" value="4" v-model="rating">
            <label for="star4" title="4 stars">★</label>
            <input type="radio" id="star3" name="rating" value="3" v-model="rating">
            <label for="star3" title="3 stars">★</label>
            <input type="radio" id="star2" name="rating" value="2" v-model="rating">
            <label for="star2" title="2 stars">★</label>
            <input type="radio" id="star1" name="rating" value="1" v-model="rating">
            <label for="star1" title="1 star">★</label>
          </div>
        </div>
          <button style="background-color: #FFD700;" type="submit">Submit</button>
        </form>
      </div>
    </div>
  `,
  props: ['username','influencer_id','influencer_name'],
  data() {
    return {
      sponsor_name: this.username,
      inf_id: this.influencer_id,
      influencer_name:this.influencer_name,
      rating: 0,
    };
  },
    methods: {
      closeModal() {
        console.log("Closing modal");
        this.$emit('close');
      },
      submitRating() {
        console.log("Submitting Rating");
        const rating = {
          sponsor_name: this.username,
          inf_id: this.influencer_id,
          influencer_name:this.influencer_name,
          rating: this.rating,
        };
        this.$emit('submit', rating);
        this.closeModal();
        window.location.href=`/sponsor/${this.username}/details/inf/${this.influencer_id}`;
      }
    }
});
new Vue({
  el: '#app',
  data: {
      showModal: false,
      showModal2: false,
      showModal3: false,
      showModal4: false,
      username: '',
      description: '',
      followers: 0,
      influencer_id: '',
      influencer_name: '',
      campaigns:[]
  },
  mounted() {
    this.username = this.$el.getAttribute('data-username');
    this.description = this.$el.getAttribute('data-description');
    this.followers = this.$el.getAttribute('data-followers');
    this.influencer_id = this.$el.getAttribute('data-influencer_id');
    this.influencer_name = this.$el.getAttribute('data-influencer_name');
    try {
      this.campaigns = JSON.parse(this.$el.getAttribute('data-campaigns'));
  } catch (e) {
      console.error('Failed to parse campaigns:', e);
      this.campaigns = [];
  }
    
    
  },
  methods: {
      addCampaign(campaign) {
          console.log("Adding campaign", campaign);
          const url = `/sponsor/${this.username}/add_new_campaign`;
          fetch(url, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(campaign),
          })
          .then(response => response.json())
          .then(data => {
              console.log('Campaign added:', data);
          })
          .catch((error) => {
              console.error('Error:', error);
          });
      },

      editCampaign(campaign) {
        console.log("Editing campaign", campaign);
        const url = `/sponsor/${this.username}/edit_campaign/${campaign["id"]}`;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(campaign),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Campaign added:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    },

    editDesc(desc) {
        console.log("Editing..", desc);
        const url = `/inf/edit_desc/${this.username}`;
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(desc),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Desc Saved', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    },

    editFoll(foll) {
      console.log("Editing..", foll);
      const url = `/inf/edit_followers/${this.username}`;
      fetch(url, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(foll),
      })
      .then(response => response.json())
      .then(data => {
          console.log('Followers Saved', data);
      })
      .catch((error) => {
          console.error('Error:', error);
      });
  },

  editEmail(email) {
    console.log("Editing..", email);
    const url = `/inf/edit_email/${this.username}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(email),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Email Saved', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
  },

  editspEmail(email) {
    console.log("Editing..", email);
    const url = `/sponsor/edit_email/${this.username}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(email),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Email Saved', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
  },

  editCategory(category) {
    console.log("Editing..", category);
    const url = `/inf/edit_category/${this.username}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(category),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Followers Saved', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
  },

  editspCategory(category) {
    console.log("Editing..", category);
    const url = `/sponsor/edit_category/${this.username}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(category),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Followers Saved', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
  },
  sendRequest(request) {
    console.log(request);
    const url = `/sponsor/${request['sp_name']}/details/inf/${request['inf_id']}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message) });
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
  },
  sendRequest_byinf(req) {
    console.log(req);
    const url = `/influencer/${req['inf_name']}/details/camp/${req['campaign_id']}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(req),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message) });
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
  },
  sendRating(rating) {
    console.log(rating);
    const url = `/sponsor/${rating['sponsor_name']}/rate/inf/${rating['inf_id']}`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(rating),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.message) });
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
  },
  },
});

console.log("VUE LOADED SUCCESSFULLY");
