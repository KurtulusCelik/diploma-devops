from datetime import date
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    def validate_title(self, value: str):
        if value is None:
            return value
        trimmed = value.strip()
        if trimmed == "":
            raise serializers.ValidationError("Title cannot be blank")
        
        has_alnum = False
        for char in trimmed:
            if char.isalnum():
                has_alnum = True
                break
        if not has_alnum:
            raise serializers.ValidationError("Title must contain at least one letter or digit")

        return value

    def validate_author(self, value: str):
        if value is None:
            return value
        trimmed = value.strip()
        if trimmed == "":
            raise serializers.ValidationError("Author cannot be blank")
        
        has_letter = False
        for char in trimmed:
            if char.isalpha():
                has_letter = True
                break
        if not has_letter:
            raise serializers.ValidationError("Author must contain at least one letter")

        for char in trimmed:
            if not char.isalpha() and not char.isspace():
                raise serializers.ValidationError("Author can contain only letters and spaces")
        
        return value

    def validate_isbn(self, value: str):
        if value is None or value == "":
            return value

        digits = []
        for char in value:
            if char.isdigit():
                digits.append(char)

        if len(digits) not in (10, 13):
            raise serializers.ValidationError("ISBN must contain 10 or 13 digits (ISBN-10/ISBN-13)")
        return value

    def validate_published_date(self, value):
        if value is None:
            return value
        if value > date.today():
            raise serializers.ValidationError("Published date cannot be in the future")
        return value

    class Meta:
        model = Book
        fields = ['title', 'description', 'author', 'isbn', 'published_date']