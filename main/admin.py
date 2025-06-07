from django.contrib import admin

from .models import Category, Report, Video, Comment
from .views import delete_video, hide_video


@admin.action(description="Delete this bullshit")
def delete_reported_video(modeladmin, request, queryset):
    for report in queryset:
        if report.video:
            delete_video(report.video)


delete_reported_video.short_description = 'Удалить видео из выделенных жалоб'

@admin.action(description='Hide this bullshit')
def hide_reported_video(modeladmin, request, queryset):
    for report in queryset:
        if report.video:
            hide_video(report.video)
            report.delete()

hide_reported_video.short_description = 'Скрыть видео для дальнейшего удаления'

@admin.action(description="Delete this commentary")
def delete_reported_comment(modeladmin, request, queryset):
    for report in queryset:
        if report.comment:
            report.comment.delete()


delete_reported_comment.short_description = 'Удалить комментарии из выделенных жалоб'

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_target', 'reason_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('reason', 'user__username')
    actions = [hide_reported_video, delete_reported_comment]

    def get_target(self, obj):
        return obj.video or obj.comment

    def reason_short(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason

    get_target.short_decsription = 'На что пожаловались'
    reason_short.short_description = 'Причина'