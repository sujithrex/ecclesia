from django.contrib import admin
from .models import (
    Pastorate, Church, Area, Fellowship, Family, Member,
    Respect, Relation
)

@admin.register(Pastorate)
class PastorateAdmin(admin.ModelAdmin):
    list_display = ('pastorate_name', 'pastorate_short_name', 'user', 'created_at', 'updated_at')
    search_fields = ('pastorate_name', 'pastorate_short_name')
    list_filter = ('created_at', 'updated_at')
    ordering = ('pastorate_name',)

@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ('church_name', 'short_name', 'pastorate', 'created_at', 'updated_at')
    search_fields = ('church_name', 'short_name')
    list_filter = ('pastorate', 'created_at', 'updated_at')
    ordering = ('church_name',)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('area_name', 'area_id', 'church', 'created_at', 'updated_at')
    search_fields = ('area_name', 'area_id')
    list_filter = ('church', 'created_at', 'updated_at')
    ordering = ('area_id',)

@admin.register(Fellowship)
class FellowshipAdmin(admin.ModelAdmin):
    list_display = ('fellowship_name', 'fellowship_id', 'area', 'get_church', 'created_at', 'updated_at')
    search_fields = ('fellowship_name', 'fellowship_id', 'address')
    list_filter = ('area__church', 'area', 'created_at', 'updated_at')
    ordering = ('fellowship_id',)

    def get_church(self, obj):
        return obj.area.church
    get_church.short_description = 'Church'
    get_church.admin_order_field = 'area__church'

@admin.register(Respect)
class RespectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('family_head', 'family_id', 'area', 'fellowship', 'mobile', 'created_at')
    search_fields = ('family_head', 'family_id', 'mobile', 'email')
    list_filter = ('area', 'fellowship', 'respect')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['respect', 'area', 'fellowship']

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_id', 'family', 'relation', 'age', 'baptised', 'conformed')
    search_fields = ('name', 'member_id', 'aadhar_number')
    list_filter = ('baptised', 'conformed', 'death', 'sex', 'respect', 'relation')
    readonly_fields = ('age', 'created_at', 'updated_at')
    autocomplete_fields = ['family', 'respect', 'relation']
    fieldsets = (
        ('Basic Information', {
            'fields': ('family', 'member_id', 'aadhar_number', 'respect', 'initial', 'name', 'relation', 'sex', 'image')
        }),
        ('Dates', {
            'fields': ('dob', ('age',), 'dom')
        }),
        ('Work Information', {
            'fields': ('working', 'working_place')
        }),
        ('Church Information', {
            'fields': (('baptised', 'date_of_bap'), ('conformed', 'date_of_conf'))
        }),
        ('Death Information', {
            'fields': (('death', 'date_of_death'),)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
