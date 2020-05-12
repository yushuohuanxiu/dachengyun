"""dachengyunsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from dachengyun import userOperate
from dachengyun import manageOperate
from dachengyun import fileSync

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', userOperate.register),
    path('manage/userDel/', manageOperate.userDel),
    path('manage/syncFolerDel/', manageOperate.syncFolerDel),
    path('manage/userPrivilegeDel/', manageOperate.userPrivilegeDel),
    path('manage/queryUserList/', manageOperate.queryUserList),
    path('manage/querySyncFolderList/', manageOperate.querySyncFolderList),
    path('manage/queryPrivilegeList/', manageOperate.queryPrivilegeList),
    path('manage/userAdd/', manageOperate.userAdd),
    path('manage/syncFolderAdd/', manageOperate.syncFolderAdd),
    path('manage/userPrivilegeAdd/', manageOperate.userPrivilegeAdd),
    path('manage/userPasswordRefresh/', manageOperate.userPasswordRefresh),
    path('sync/querySyncFolder/', fileSync.querySyncFolder),
    path('sync/queryFileInfo/', fileSync.queryFileInfo),
    path('sync/queryFileInfoWithLock/', fileSync.queryFileInfoWithLock),
    path('sync/releaseLock/', fileSync.releaseLock),
    path('sync/syncFile/', fileSync.syncFile),
    path('', TemplateView.as_view(template_name='index.html')),
]
