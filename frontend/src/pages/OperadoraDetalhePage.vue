<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";
import { getOperadora, getDespesas, type DespesaHistorico, type Operadora } from "../services/api";

const route = useRoute();
const loading = ref(false);
const error = ref("");
const operadora = ref<Operadora | null>(null);
const despesas = ref<DespesaHistorico[]>([]);
const brlFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

function formatCurrency(value: number) {
  return brlFormatter.format(value);
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const cnpj = String(route.params.cnpj || "");
    if (!cnpj) {
      throw new Error("CNPJ inválido.");
    }
    operadora.value = await getOperadora(cnpj);
    const hist = await getDespesas(cnpj);
    despesas.value = hist.data || [];
  } catch {
    error.value = "Falha ao carregar detalhes.";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="grid">
    <router-link to="/">← Voltar</router-link>
    <section class="card" v-if="loading">
      <ProgressSpinner style="width: 32px; height: 32px" strokeWidth="6" />
    </section>
    <Message v-else-if="error" severity="error">{{ error }}</Message>

    <template v-else-if="operadora">
      <section class="card">
        <h2>{{ operadora.RazaoSocial }}</h2>
        <p><strong>CNPJ:</strong> {{ operadora.CNPJ }}</p>
        <p><strong>Registro ANS:</strong> {{ operadora.RegistroANS }}</p>
        <p><strong>UF:</strong> {{ operadora.UF || "-" }}</p>
      </section>

      <section class="card">
        <h2>Histórico de despesas</h2>
        <DataTable :value="despesas" tableStyle="min-width: 30rem">
          <Column field="Ano" header="Ano" />
          <Column field="Trimestre" header="Trimestre" />
          <Column header="Valor">
            <template #body="{ data }">
              {{ formatCurrency(Number(data.ValorDespesas || 0)) }}
            </template>
          </Column>
        </DataTable>
      </section>
    </template>
  </section>
</template>
