<script setup lang="ts">
import { onMounted, ref } from "vue";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Message from "primevue/message";
import Paginator from "primevue/paginator";
import ProgressSpinner from "primevue/progressspinner";
import OperadorasTable from "../components/OperadorasTable.vue";
import UfChart from "../components/UfChart.vue";
import { getOperadoras, type Operadora } from "../services/api";

const loading = ref(false);
const error = ref("");
const search = ref("");
const page = ref(1);
const limit = ref(10);
const total = ref(0);
const operadoras = ref<Operadora[]>([]);

type PaginatorEvent = {
  page: number;
  rows: number;
};

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const res = await getOperadoras({
      page: page.value,
      limit: limit.value,
      search: search.value,
    });
    operadoras.value = res.data;
    total.value = res.total;
  } catch {
    error.value = "Falha ao carregar operadoras.";
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  page.value = 1;
  load();
}

function onPage(event: PaginatorEvent) {
  page.value = event.page + 1;
  limit.value = event.rows;
  load();
}

onMounted(load);
</script>

<template>
  <section class="grid">
    <section class="card">
      <h2>Busca</h2>
      <div class="toolbar">
        <InputText
          v-model="search"
          placeholder="Buscar por CNPJ ou Razão Social"
          @keyup.enter="handleSearch"
        />
        <Button label="Buscar" @click="handleSearch" />
      </div>
      <div v-if="loading" class="loading">
        <ProgressSpinner style="width: 32px; height: 32px" strokeWidth="6" />
      </div>
      <Message v-else-if="error" severity="error">{{ error }}</Message>
      <p v-else>Total: {{ total }}</p>
    </section>

    <OperadorasTable :rows="operadoras" />
    <UfChart :operadoras="operadoras" />

    <section class="card pager">
      <Paginator
        :first="(page - 1) * limit"
        :rows="limit"
        :totalRecords="total"
        :rowsPerPageOptions="[10, 20, 50]"
        @page="onPage"
      />
    </section>
  </section>
</template>
