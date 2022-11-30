import time

from ParserModules.BaseParser import BaseParser, ErrorOpenUrl
from ParserModules.ChannelPostsParser import ChannelPostsParser
from ParserModules.FollowersParser import FollowersParser
from ParserModules.UserCommentsAndLikesParser import PostCommentsAndLikesParser
from ParserModules.UserFriendsParser import UserFriendsParser
from ParserModules.UserProfileParser import ServiceData, UserProfileParser
from ParserModules.VideoParser import VideoParser

if __name__ == "__main__":
    try:
        sd = ServiceData(
            # logins=('https://my.mail.ru/mail/artem_yakovlev/', ),
            logins=('https://my.mail.ru/community/kcinema/multipost/9D15000093CE0005.html', ),
            # logins=('https://my.mail.ru/v/nikavideo1989/video/9/978.html', 'https://my.mail.ru/v/topclips/video/alltop/60393.html'),
            task_id='',
            free_thread_id=1,
            task_type="5"
        )
        data = PostCommentsAndLikesParser(sd).launch()
        print(data)

    except ErrorOpenUrl:
        # logger.warning("ErrorOpenUrl, see input links")
        print('error, closing driver')
