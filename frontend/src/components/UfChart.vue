<script setup lang="ts">
import { computed, type PropType } from "vue";
import Chart from "primevue/chart";
import type { Operadora } from "../services/api";

const props = defineProps({
  operadoras: {
    type: Array as PropType<Operadora[]>,
    default: () => [],
  },
});

const brlFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

function formatCurrency(value: number) {
  return brlFormatter.format(value);
}

const byUf = computed(() => {
  const map = new Map();
  for (const op of props.operadoras) {
    const uf = op.UF || "N/A";
    const current = map.get(uf) || 0;
    map.set(uf, current + Number(op.TotalDespesas || 0));
  }
  return [...map.entries()].sort((a, b) => b[1] - a[1]).slice(0, 10);
});

const chartData = computed(() => ({
  labels: byUf.value.map(([uf]) => uf),
  datasets: [
    {
      label: "Total de despesas por UF",
      data: byUf.value.map(([, total]) => total),
      backgroundColor: "#22c55e",
      borderRadius: 6,
    },
  ],
}));

const chartOptions = {
  scales: {
    y: {
      ticks: {
        callback: (value: string | number) => formatCurrency(Number(value)),
      },
    },
  },
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: (context: { parsed: { y: number } }) => formatCurrency(context.parsed.y),
      },
    },
  },
  maintainAspectRatio: false,
};
</script>

<template>
  <section class="card">
    <h2>Distribuição de despesas por UF</h2>
    <div>
      <Chart type="bar" :data="chartData" :options="chartOptions" />
    </div>
  </section>
</template>
