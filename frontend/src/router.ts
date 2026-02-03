import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";
import OperadorasPage from "./pages/OperadorasPage.vue";
import OperadoraDetalhePage from "./pages/OperadoraDetalhePage.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", component: OperadorasPage },
  { path: "/operadoras/:cnpj", component: OperadoraDetalhePage, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
