<link rel="stylesheet" href="/static/style.css">
<div class="box">
<h2>Edit Profile</h2>
<form method="post" enctype="multipart/form-data">
<textarea name="bio">{{ user.bio }}</textarea>
<input type="file" name="profile_pic">
<button>Save</button>
</form>
</div>