from blog.models.post import Post

class PostRepository():

    @staticmethod
    def get_all():
        return Post.objects.all()
    
    @staticmethod
    def get_by_id(id):
        try:
            return Post.objects.get(id = id)
        except Post.DoesNotExist:
            return None
        
    @staticmethod
    def create(data):
        return Post.objects.create(**data)
        
    @staticmethod
    def update(post, data):
        for key, value in data.items():
            setattr(post, key, value)
        post.save()
        return post

    @staticmethod
    def delete(post):
        post.delete()
