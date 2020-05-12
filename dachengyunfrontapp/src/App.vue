<template>
    <div id="app">

        <b-navbar toggleable="lg" type="dark" variant="info">
            <b-navbar-brand>dachengyun Setting Page</b-navbar-brand>
        </b-navbar>
        <b-container fluid style="padding-top: 30px; padding-left: 30px; padding-right: 30px">
            <b-row>
                <b-col>
                    <b-card header-tag="header">
                        <template v-slot:header>
                            <p class="h4">
                                同步文件夹列表
                                <b-icon icon="folder-plus" @click="$bvModal.show('modal-folderAdd')"
                                        style="float: right" font-scale="1.4"></b-icon>
                            </p>
                        </template>

                        <b-table style="margin-bottom: 0px;"
                                 :items="folderItems"
                                 :fields="folderFields"
                                 head-variant="dark"
                                 stacked="md"
                                 hover
                                 striped
                                 bordered
                        >
                            <template v-slot:cell(userCount)="row">
                                {{row.item.userCount}}
                                <b-icon icon="trash"
                                        style="float: right; padding-top: 5px;"
                                        font-scale="1.4"
                                        @click.stop="onFolderDelete(row.item)"
                                ></b-icon>
                            </template>
                        </b-table>

                    </b-card>
                </b-col>
                <b-col cols="4">
                    <b-card header-tag="header">
                        <template v-slot:header>
                            <p class="h4">
                                用户列表
                                <b-icon icon="person-plus" @click="$bvModal.show('modal-userAdd')"
                                        style="float: right" font-scale="1.4"></b-icon>
                            </p>
                        </template>
                        <b-table style="margin-bottom: 0px;"
                                 :items="userItems"
                                 :fields="userFields"
                                 head-variant="dark"
                                 stacked="md"
                                 hover
                                 striped
                                 bordered
                        >
                            <template v-slot:cell(clientCount)="row">
                                {{row.item.clientCount}}
                                <b-icon icon="trash"
                                        style="float: right; padding-top: 5px;"
                                        font-scale="1.4"
                                        @click.stop="onUserDelete(row.item)"
                                ></b-icon>
                                <b-icon icon="arrow-repeat"
                                        style="float: right; padding-top: 5px;"
                                        font-scale="1.4"
                                        @click.stop="onUserPasswordRefresh(row.item)"
                                ></b-icon>
                            </template>
                        </b-table>
                    </b-card>
                </b-col>

                <b-col cols="5">
                    <b-card header-tag="header">
                        <template v-slot:header>
                            <p class="h4">
                                权限列表
                                <b-icon icon="file-plus" @click="$bvModal.show('modal-privilegeAdd')"
                                        style="float: right" font-scale="1.4"></b-icon>
                            </p>
                        </template>
                        <b-table style="margin-bottom: 0px;"
                                 :items="privilegeItems"
                                 :fields="privilegeFields"
                                 head-variant="dark"
                                 stacked="md"
                                 hover
                                 striped
                                 bordered
                        >
                            <template v-slot:cell(privilege)="row">
                                {{privilegeFormat(row.item)}}
                                <b-icon icon="trash"
                                        style="float: right; padding-top: 5px;"
                                        font-scale="1.4"
                                        @click.stop="onPrivilegeDelete(row.item)"
                                ></b-icon>
                            </template>
                        </b-table>
                    </b-card>
                </b-col>
            </b-row>
        </b-container>

        <b-modal id="modal-userAdd" title="添加用户"
                 @hidden="resetModal('user')" @ok="userAdd">
            <b-form ref="userAdd" validated>
                <b-form-group label="用户名：" invalid-feedback="请输入最小3位字母或数字组合的用户名信息">
                    <b-form-input v-model="user.username" placeholder="请输入用户名"
                                  required pattern="[A-Za-z0-9]{3,30}"></b-form-input>
                </b-form-group>
            </b-form>
        </b-modal>

        <b-modal id="modal-folderAdd" title="添加共享文件夹"
                 @hidden="resetModal('folder')" @ok="folderAdd">
            <b-form ref="folderAdd" validated>
                <b-form-group label="文件夹名：" invalid-feedback="请输入最小2位汉字、字母或数字组合的同步文件夹名信息">
                    <b-form-input v-model="folder.foldername" placeholder="请输入同步文件夹名"
                                  required pattern="[A-Za-z0-9\u4e00-\u9fa5]{2,30}"></b-form-input>
                </b-form-group>
            </b-form>
        </b-modal>

        <b-modal id="modal-privilegeAdd" title="添加权限"
                 @hidden="resetModal('privilege')" @ok="privilegeAdd">
            <b-form ref="privilegeAdd" validated>
                <b-form-group label="文件夹名：" invalid-feedback="请选择同步文件夹">
                    <b-form-select
                            v-model="privilege.foldername"
                            :options="folderItems"
                            class="mb-3"
                            value-field="foldername"
                            text-field="foldername"
                            required
                    >
                        <template v-slot:first>
                            <b-form-select-option :value="null" disabled>-- 请选择同步文件夹 --</b-form-select-option>
                        </template>
                    </b-form-select>
                </b-form-group>

                <b-form-group label="用户名：" invalid-feedback="请选择用户">
                    <b-form-select
                            v-model="privilege.username"
                            :options="userItems"
                            class="mb-3"
                            value-field="username"
                            text-field="username"
                            required
                    >
                        <template v-slot:first>
                            <b-form-select-option :value="null" disabled>-- 请选择用户 --</b-form-select-option>
                        </template>
                    </b-form-select>
                </b-form-group>


                <b-form-group label="权限：" invalid-feedback="请选择权限">
                    <b-form-select v-model="privilege.privilege"
                                   class="mb-3"
                                   required>
                        <b-form-select-option :value="null" disabled>-- 请选择权限 --</b-form-select-option>
                        <b-form-select-option value="3">读取</b-form-select-option>
                        <b-form-select-option value="2">读取、修改</b-form-select-option>
                        <b-form-select-option value="1">读取、修改、新建</b-form-select-option>
                        <b-form-select-option value="0">读取、修改、新建、删除</b-form-select-option>
                    </b-form-select>
                </b-form-group>
            </b-form>
        </b-modal>

    </div>
</template>
<script>

    export default {
        data() {
            return {
                userFields: [
                    {key: 'username', label: '用户名', sortable: true},
                    {key: 'password', label: '密码'},
                    {key: 'clientCount', label: '终端数'},
                ],
                userItems: [],
                folderFields: [
                    {key: 'foldername', label: '文件夹名', sortable: true},
                    {key: 'userCount', label: '用户数'}],
                folderItems: [],
                privilegeFields: [
                    {key: 'foldername', label: '文件夹名', sortable: true},
                    {key: 'username', label: '用户名', sortable: true},
                    {key: 'privilege', label: '权限'}],
                privilegeItems: [],
                user: {
                    username: null
                },
                folder: {
                    foldername: null
                },
                privilege: {
                    foldername: null,
                    username: null,
                    privilege: null
                }
            }
        },
        mounted() {
            this.$reflush()
        },
        methods: {
            onUserDelete(item) {
                this.$bvModal.msgBoxConfirm('是否要删除用户[' + item.username + ']?', {
                    title: '删除确认',
                    buttonSize: 'sm',
                    okVariant: 'danger',
                    okTitle: '删除',
                    cancelTitle: '取消',
                    headerClass: 'p-2 border-bottom-0',
                    footerClass: 'p-2 border-top-0',
                }).then(value => {
                    if (value) {
                        this.$http.post("http://127.0.0.1:8000/manage/userDel/", JSON.stringify({username: item.username}))
                            .then(response => {
                                this.$reflush()
                            })
                    }
                })
            },
            onUserPasswordRefresh(item) {
                this.$http.post("http://127.0.0.1:8000/manage/userPasswordRefresh/", JSON.stringify({username: item.username}))
                    .then(response => {
                        this.$reflush()
                    })
            },
            onFolderDelete(item) {
                this.$bvModal.msgBoxConfirm('是否要删除文件夹[' + item.foldername + ']?', {
                    title: '删除确认',
                    buttonSize: 'sm',
                    okVariant: 'danger',
                    okTitle: '删除',
                    cancelTitle: '取消',
                    headerClass: 'p-2 border-bottom-0',
                    footerClass: 'p-2 border-top-0',
                }).then(value => {
                    if (value) {
                        this.$http.post("http://127.0.0.1:8000/manage/syncFolerDel/", JSON.stringify({foldername: item.foldername}))
                            .then(response => {
                                this.$reflush()
                            })
                    }
                })
            },
            onPrivilegeDelete(item) {
                this.$bvModal.msgBoxConfirm('是否要删除权限[' + item.foldername + '-' + item.username + ']?', {
                    title: '删除确认',
                    buttonSize: 'sm',
                    okVariant: 'danger',
                    okTitle: '删除',
                    cancelTitle: '取消',
                    headerClass: 'p-2 border-bottom-0',
                    footerClass: 'p-2 border-top-0',
                }).then(value => {
                    if (value) {
                        this.$http.post("http://127.0.0.1:8000/manage/userPrivilegeDel/", JSON.stringify({
                            username: item.username,
                            foldername: item.foldername
                        }))
                            .then(response => {
                                this.$reflush()
                            })
                    }
                })
            },
            $reflush() {
                this.$http.post("http://127.0.0.1:8000/manage/queryUserList/")
                    .then(response => {
                        this.userItems = response.data
                    })
                this.$http.post("http://127.0.0.1:8000/manage/querySyncFolderList/")
                    .then(response => {
                        this.folderItems = response.data
                    })
                this.$http.post("http://127.0.0.1:8000/manage/queryPrivilegeList/")
                    .then(response => {
                        this.privilegeItems = response.data
                    })
            },
            resetModal(modelname) {
                if (modelname == 'user') {
                    this.user.username = null
                } else if (modelname == 'folder') {
                    this.folder.foldername = null
                } else if (modelname == 'privilege') {
                    this.privilege.username = null
                    this.privilege.foldername = null
                    this.privilege.privilege = null
                }
            },
            userAdd(bvModalEvt) {
                bvModalEvt.preventDefault()
                if (!this.$refs.userAdd.checkValidity()) {
                    return
                }
                this.$http.post("http://127.0.0.1:8000/manage/userAdd/",
                    JSON.stringify(this.user))
                    .then(response => {
                        if (response.data != "ok") {
                            this.showWarnInfo(response.data)
                            return
                        }
                        this.$reflush()
                        this.$nextTick(() => {
                            this.$bvModal.hide('modal-userAdd')
                        })
                    })

            },
            folderAdd(bvModalEvt) {
                bvModalEvt.preventDefault()
                if (!this.$refs.folderAdd.checkValidity()) {
                    return
                }
                this.$http.post("http://127.0.0.1:8000/manage/syncFolderAdd/",
                    JSON.stringify(this.folder))
                    .then(response => {
                        if (response.data != "ok") {
                            this.showWarnInfo(response.data)
                            return
                        }
                        this.$reflush()
                        this.$nextTick(() => {
                            this.$bvModal.hide('modal-folderAdd')
                        })
                    })

            },
            privilegeAdd(bvModalEvt) {
                bvModalEvt.preventDefault()
                if (!this.$refs.privilegeAdd.checkValidity()) {
                    return
                }
                this.$http.post("http://127.0.0.1:8000/manage/userPrivilegeAdd/",
                    JSON.stringify(this.privilege))
                    .then(response => {
                        if (response.data != "ok") {
                            this.showWarnInfo(response.data)
                            return
                        }
                        this.$reflush()
                        this.$nextTick(() => {
                            this.$bvModal.hide('modal-privilegeAdd')
                        })
                    })

            },
            privilegeFormat(item) {
                if (item.privilege == 0) {
                    return '读取、修改、新建、删除'
                } else if (item.privilege == 1) {
                    return '读取、修改、新建'
                } else if (item.privilege == 2) {
                    return '读取、修改'
                } else if (item.privilege == 3) {
                    return '读取'
                }
            },
            showWarnInfo(info) {
                this.$bvToast.toast(info, {
                    title: '错误信息',
                    variant: 'warning',
                    solid: true,
                    autoHideDelay: 3000
                })
            }
        }
    }
</script>