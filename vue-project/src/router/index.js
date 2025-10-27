import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../pages/LoginPage.vue";
import SignupPage from "../pages/SignUpPage.vue";
import GalleryPage from "../pages/GalleryPage.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "login", component: LoginPage },
  { path: "/signup", name: "signup", component: SignupPage },
  {
    path: "/gallery",
    name: "gallery",
    component: GalleryPage,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem("token");

  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
  } else if (
    (to.path === "/login" || to.path === "/signup") &&
    isAuthenticated
  ) {
    next("/gallery"); // redirect logged-in users away from auth pages
  } else {
    next();
  }
});

export default router;
