<script setup lang="ts">

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import type { PropType } from "vue";
import type { Operadora } from "../services/api";

const brlFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

function formatCurrency(value: number) {
  return brlFormatter.format(value);
}

defineProps({
  rows: {
    type: Array as PropType<Operadora[]>,
    default: () => [],
  },
});
</script>

<template>
  <div class="card">
    <h2>Operadoras</h2>
    <div class="card">
      <DataTable :value="rows" dataKey="CNPJ" tableStyle="min-width: 50rem">
        <Column field="CNPJ" header="CNPJ">
          <template #body="{ data }">
            <router-link :to="`/operadoras/${data.CNPJ}`">{{ data.CNPJ }}</router-link>
          </template>
        </Column>
        <Column field="RazaoSocial" header="Razão Social" />
        <Column field="RegistroANS" header="Registro ANS" />
        <Column header="UF">
          <template #body="{ data }">
            {{ data.UF || "-" }}
          </template>
        </Column>
        <Column header="Total Despesas">
          <template #body="{ data }">
            {{ formatCurrency(Number(data.TotalDespesas || 0)) }}
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>
