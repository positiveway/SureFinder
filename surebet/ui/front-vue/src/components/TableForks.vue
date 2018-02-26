<template>
    <div>
        <div v-if="selected != ''">
            <div class="md-layout">
                <div class="md-layout-item">
                    <md-card>
                        <table>
                            <tr>
                                <th>Bookmaker</th>
                                <th>Bet</th>
                                <th>Odds</th>
                                <th>Bet</th>
                                <th>D</th>
                                <th>F</th>
                                <th>Profit</th>
                                <th>Rounding</th>
                            </tr>
                            <tr>
                                <td>
                                    {{ selected.book1 }}
                                </td>
                                <td>
                                    Bet 1
                                </td>
                                <td>
                                    <input v-model="message" class="sum1">
                                </td>
                                <td>
                                    <input v-model="message" class="sum1">
                                </td>
                                <td>
                                    <input type="checkbox" id="checkbox" v-model="checked">
                                </td>
                                <td>
                                    <input type="checkbox" id="checkbox" v-model="checked">
                                </td>
                                <td>
                                    profit
                                </td>
                                <td>
                                    <select v-model="selected">
                                                                  <option>1</option>
                                                                  <option>0.1</option>
                                                                  <option>0.01</option>
                                                                  <option>5</option>
                                                                  <option>10</option>
                                                                  <option>50</option>
                                                                </select>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    {{ selected.book2 }}
                                </td>
                                <td>
                                    Bet 2
                                </td>
                                <td>
                                    <input v-model="message" class="sum1">
                                </td>
                                <td>
                                    <input v-model="message" class="sum1">
                                </td>
                                <td>
                                    <input type="checkbox" v-model="checked">
                                </td>
                                <td>
                                    <input type="checkbox" v-model="checked">
                                </td>
                                <td>
                                    profit
                                </td>
                                <td>
                                    <select v-model="selected">
                                                                  <option>1</option>
                                                                  <option>0.1</option>
                                                                  <option>0.01</option>
                                                                  <option>5</option>
                                                                  <option>10</option>
                                                                  <option>50</option>
                                                            </select>
                                </td>
                            </tr>
                            <tr>
                                <td> </td>
                                <td> </td>
                                <td> </td>
                                <td>
                                    <input v-model="message" class="sum1">
                                </td>
                                <td> </td>
                                <td>
                                    <input type="checkbox" v-model="checked">
                                </td>
                            </tr>
                        </table>
                        Surebet coeffecent: {{ 1/selected.w1['0'].factor + 1/selected.w2['0'].factor}}
                    </md-card>
                </div>
            </div>
        </div>
        <md-field v-if="urlAPI === '' ">
            <label>Paste url API</label>
            <md-input v-model="urlAPI"></md-input>
            <span class="md-helper-text">surefuck.com/  api.json</span>
        </md-field>
        <md-button v-else v-on:click="getdata">Update</md-button>
        <md-table v-if="bapi != ''" v-model="bapi" md-card @md-selected="onSelect" md-sort-order="asc">
            <md-table-row slot="md-table-row" slot-scope="{ item }" class="md-primary" md-selectable="single" @md-selected="onSelect">
                <md-table-cell md-label="Bookmeker"> {{ item.book1 }} <br> {{ item.book2 }} </md-table-cell>
    
                <md-table-cell md-label="Lifetime">{{ item.lifetime }} </md-table-cell>
    
                <md-table-cell md-label="Part"> {{ item.part }} </md-table-cell>
    
                <md-table-cell md-label="Profit"> {{ item.profit }} </md-table-cell>
    
                <md-table-cell md-label="Sport"> {{ item.sport }} </md-table-cell>
    
                <md-table-cell md-label="Teams">
                    {{ item.teams1 }}
                    <br> {{ item.teams2 }}
                </md-table-cell>
    
                <md-table-cell md-label="W">
                    {{ item.w1[0].cond }} / {{ item.w1[0].factor }} / {{ item.w1[0].name }} / {{ item.w1[0].suffix }}
                    <br> {{ item.w2[0].cond }} / {{ item.w2[0].factor }} / {{ item.w2[0].name }} / {{ item.w2[0].suffix }}
                </md-table-cell>
            </md-table-row>
        </md-table>
    </div>
</template>

<script>
    import axios from 'axios'
    export default {
        name: 'TableForks',
        data() {
            return {
                selected: '',
                bapi: '',
                timer: '',
                urlAPI: ''
            }
        },
        methods: {
            onSelect(item) {
                this.selected = item
            },
            getdata: function() {
                axios.get(this.urlAPI)
                    .then(response => {
                        this.bapi = response.data
                    }).catch(e => {
                        this.errors.push(e)
                    })
            }
        }
    }
</script>

<style>
    .sum1 {
        width: 45px;
    }
</style>

